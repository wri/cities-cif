import ee
import geopandas as gpd
import numpy as np
import xarray as xr
from rasterio.enums import Resampling
from datetime import datetime

import rpy2.robjects as ro
from rpy2.robjects import default_converter, pandas2ri
from rpy2.robjects.packages import importr
from rpy2.robjects.conversion import localconverter
from rasterio.features import rasterize
from rasterio.transform import from_origin

from city_metrix.constants import GTIFF_FILE_EXTENSION
from city_metrix.metrix_model import Layer, GeoExtent, validate_raster_resampling_method
from city_metrix.metrix_dao import extract_bbox_aoi
from city_metrix.metrix_tools import is_date
from .era5_hottest_day_gee import find_hottest_date, DEFAULT_SPATIAL_RESOLUTION

ERA5_DEFAULT_SPATIAL_RESOLUTION = DEFAULT_SPATIAL_RESOLUTION
DEFAULT_SPATIAL_RESOLUTION = 200
DEFAULT_RESAMPLING_METHOD = 'bilinear'


class BuAirTemperature(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, start_date: str = None, end_date: str = None, single_data: str = None,
                 seasonal_utc_offset: float = 0, sampling_local_hours: str = '', **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.single_date = single_data
        self.seasonal_utc_offset = seasonal_utc_offset
        self.sampling_local_hours = sampling_local_hours

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method: str = DEFAULT_RESAMPLING_METHOD):
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)
        if self.single_date:
            if not is_date(self.single_date):
                raise Exception(f"Invalid single_date: {self.single_date}")
        else:
            if not is_date(self.start_date) or not is_date(self.end_date):
                raise Exception(
                    f"Invalid date specification: start_date:{self.start_date}, end_date:{self.end_date}.")

        buffered_utm_bbox = bbox.buffer_utm_bbox(10)
        geographic_bbox = buffered_utm_bbox.as_geographic_bbox()

        geographic_centroid = geographic_bbox.centroid
        center_lon = geographic_centroid.x
        center_lat = geographic_centroid.y

        dataset_land = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY")

        if self.start_date is not None and self.end_date is not None:
            local_date = find_hottest_date(center_lon, center_lat, ERA5_DEFAULT_SPATIAL_RESOLUTION, geographic_bbox, dataset_land,
                                           self.start_date, self.end_date, self.seasonal_utc_offset)
            doy = local_date.timetuple().tm_yday
        elif self.single_date is not None:
            doy = datetime.strptime(
                self.single_date, "%Y-%m-%d").timetuple().tm_yday

        # --- R dependencies (install if missing) ---
        base = importr("base")
        bu_pkg = "smithCEE2025"
        if not bool(base.requireNamespace(bu_pkg, quietly=True)[0]):
            remotes = importr("remotes")
            remotes.install_github(
                "cmilando/smithCEE2025", build_vignettes=True, force=True)

        smith = importr("smithCEE2025")
        terra = importr("terra")
        sf = importr("sf")

        # --- Run model + apply what-if raster ---
        bos = smith.retrieve_output()

        image_path = ro.r(
            'system.file("extdata", "treeCanopy_sample.tif", package="smithCEE2025")')
        tree_raster = terra.rast(image_path)

        new_bos = smith.what_if(bos, "tree_fraction", tree_raster)

        features_r = new_bos.rx2("features")
        features_df = pandas2ri.rpy2py(features_r)

        # --- Convert sf geometry to WKT + join back ---
        shp_sf = new_bos.rx2("shapefile")

        # Convert geometry to WKT in R, then drop sf class -> plain data.frame
        r_df_wkt = ro.r("""
            function(x){
            x$geometry_wkt <- sf::st_as_text(sf::st_geometry(x))
            sf::st_geometry(x) <- NULL
            as.data.frame(x)
            }
        """)(shp_sf)

        with localconverter(default_converter + pandas2ri.converter):
            shp_df = ro.conversion.rpy2py(r_df_wkt)

        joined = features_df.merge(
            shp_df, on="id", how="left", suffixes=("", "_shp"))

        # --- Filter slice ---
        array_list = []
        for hod in [int(h) for h in self.sampling_local_hours.split(",")]:
            joined_hod = joined.loc[(joined["hod"] == hod) & (
                joined["doy"] == doy)].copy()

            joined_hod_gdf = gpd.GeoDataFrame(
                joined_hod,
                geometry=gpd.GeoSeries.from_wkt(joined_hod["geometry_wkt"]),
                crs="EPSG:4326"  # change if your CRS is different
            )

            value_col = "air_temp_baseline"

            # GeoDataFrame extent
            xmin, ymin, xmax, ymax = joined_hod_gdf.total_bounds

            # Estimate "native" polygon spacing from polygon bounds (median is robust to a few weird geometries)
            # DataFrame with minx, miny, maxx, maxy
            bounds = joined_hod_gdf.geometry.bounds
            poly_w = (bounds["maxx"] - bounds["minx"]).median()
            poly_h = (bounds["maxy"] - bounds["miny"]).median()

            xres = round(poly_w, 6)
            yres = round(poly_h, 6)

            ncol = int(np.ceil((xmax - xmin) / xres))
            nrow = int(np.ceil((ymax - ymin) / yres))

            transform = from_origin(xmin, ymax, xres, yres)

            # Rasterize
            shapes = ((geom, val) for geom, val in zip(
                joined_hod_gdf.geometry, joined_hod_gdf[value_col]))

            arr = rasterize(
                shapes=shapes,
                out_shape=(nrow, ncol),
                transform=transform,
                fill=np.nan,
                dtype="float32",
            )

            # Build coords (cell centers)
            xs = xmin + xres * (0.5 + np.arange(ncol))
            ys = ymax - yres * (0.5 + np.arange(nrow))

            da = xr.DataArray(
                arr,
                dims=("y", "x"),
                coords={"x": xs, "y": ys},
                name=value_col,
                attrs={"crs": joined_hod_gdf.crs.to_string(
                ) if joined_hod_gdf.crs else None},
            )

            utm_bbox = bbox.as_utm_bbox()
            utm_crs = utm_bbox.crs

            da_utm = da.rio.reproject(
                utm_crs, resolution=spatial_resolution, resampling=Resampling[resampling_method])

            # Trim back to original AOI
            result_data = extract_bbox_aoi(da_utm, bbox)
            result_data = result_data.expand_dims(time=[hod])

            array_list.append(result_data)

        result = xr.concat(array_list, dim="time")

        return result
