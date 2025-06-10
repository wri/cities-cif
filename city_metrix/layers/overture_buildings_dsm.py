import numpy as np
from scipy.stats import mode
import rasterio.features
import xarray as xr
import geopandas as gpd

from city_metrix.metrix_model import Layer, GeoExtent, validate_raster_resampling_method
from . import FabDEM
from .overture_buildings_w_height import OvertureBuildingsHeight
from ..constants import GTIFF_FILE_EXTENSION


DEFAULT_SPATIAL_RESOLUTION = 1
DEFAULT_RESAMPLING_METHOD = "bilinear"


# This value was determined from a large warehouse as a worst-case example at lon/lat -122.76768,45.63313
BUILDING_INCLUSION_BUFFER_METERS = 500


class OvertureBuildingsDSM(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["city"]
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        city: city id from https://sat-io.earthengine.app/view/ut-globus
    """

    def __init__(self, city="", **kwargs):
        super().__init__(**kwargs)
        self.city = city

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method: str = DEFAULT_RESAMPLING_METHOD):
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)

        # Minimize the probability that buildings will bridge tile boundaries and thereby sample elevations for
        # only part of the full footprint by: 1. buffering out AOI, 2. filtering buildings to contained buildings,
        # 3. masking buffered DEM by footprint and determining elevation of footprint, 4. masking unbuffered DEM
        # with footprint, 5. add footprint elevation to unbuffered DEM.
        # Population of the unbuffered DEM ensures that AOI is correct.
        building_buffer = BUILDING_INCLUSION_BUFFER_METERS
        buffered_utm_bbox = bbox.buffer_utm_bbox(building_buffer)

        # Load buildings and sub-select to ones fully contained in buffered area
        raw_buildings_gdf = OvertureBuildingsHeight(self.city).get_data(buffered_utm_bbox)
        contained_buildings_gdf = (
            raw_buildings_gdf)[raw_buildings_gdf.geometry.apply(lambda x: x.within(buffered_utm_bbox.polygon))]

        fab_dem = FabDEM().get_data(buffered_utm_bbox, spatial_resolution=spatial_resolution, resampling_method=resampling_method)
        query_dem = FabDEM().get_data(bbox, spatial_resolution=spatial_resolution, resampling_method=resampling_method)
        
        # rasterize building IDs
        building_id = (
            (geom, idx)
            for idx, geom in enumerate(contained_buildings_gdf.geometry, start=1)
        )
        building_id_raster = rasterio.features.rasterize(
            building_id,
            out_shape=fab_dem.shape,
            transform=fab_dem.rio.transform(),
            fill=0,
            dtype="int32",
        )
        
        # rasterize building heights
        building_height = (
            (geom, h)
            for geom, h in zip(contained_buildings_gdf.geometry, contained_buildings_gdf.height)
        )
        building_height_raster = rasterio.features.rasterize(
            building_height,
            out_shape=fab_dem.shape,
            transform=fab_dem.rio.transform(),
            fill=0,
            dtype=fab_dem.dtype,
        )

        # compute per-building DEM mode
        mode_raster = fab_dem.values.copy()
        # find all building IDs present
        for bid in np.unique(building_id_raster):
            if bid == 0:
                continue  # skip background
            mask = building_id_raster == bid
            vals = fab_dem.values[mask]
            if vals.size:
                mode_val = mode(vals, nan_policy="omit").mode
                mode_raster[mask] = mode_val
        
        # add height to the ground-mode
        result_dem_val = mode_raster + building_height_raster

        # wrap back into xarray, clip & reproject
        buffered_result = xr.DataArray(
            result_dem_val,
            coords=fab_dem.coords,
            dims=fab_dem.dims,
            attrs=fab_dem.attrs,
        ).rio.write_crs(fab_dem.rio.crs)

        clipped = buffered_result.rio.clip([bbox.as_utm_bbox().polygon])
        result_dem = query_dem.copy(data=clipped)

        return result_dem
