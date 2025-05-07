import numpy as np
import rasterio
import xarray as xr
from exactextract import exact_extract
from rasterio.features import rasterize

from city_metrix.metrix_model import Layer, GeoExtent, validate_raster_resampling_method
from . import NasaDEM
from ..constants import GTIFF_FILE_EXTENSION
from .overture_buildings_w_height import OvertureBuildingsHeight

DEFAULT_SPATIAL_RESOLUTION = 1
DEFAULT_RESAMPLING_METHOD = 'bilinear'

class OvertureBuildingsDSM(Layer):
    GEOSPATIAL_FILE_FORMAT = GTIFF_FILE_EXTENSION
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
                 resampling_method:str=DEFAULT_RESAMPLING_METHOD):
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)

        # Load the building footprints and heights
        buildings_gdf = OvertureBuildingsHeight(self.city).get_data(bbox)

        # Buffer the bbox for DEM to avoid computing footprint elevation from only elevations in the local tile
        buffet_offset_m = 100
        initial_bbox = bbox.as_utm_bbox().bounds
        buffered_west = initial_bbox[0] - buffet_offset_m
        buffered_south = initial_bbox[1] - buffet_offset_m
        buffered_east = initial_bbox[2] + buffet_offset_m
        buffered_north = initial_bbox[3] + buffet_offset_m
        buffered_geo_extent = GeoExtent()
        dem_da = NasaDEM().get_data(bbox, spatial_resolution=spatial_resolution, resampling_method=resampling_method)

        # Calculate mode elevation and estimate building elevations
        buildings_gdf['mode_elevation'] = (
            exact_extract(dem_da, buildings_gdf, ["mode"], output='pandas')['mode']
        )
        buildings_gdf["elevation_estimate"] = buildings_gdf["height"] + buildings_gdf["mode_elevation"]

        # Rasterize polygons to create a building elevation raster
        overture_buildings_raster = _rasterize_polygons(buildings_gdf, values=["elevation_estimate"],
                                                        snap_to_raster=dem_da)

        # Combine building raster with DEM
        target_crs = dem_da.rio.crs
        composite_bldg_dem = _combine_building_and_dem(dem_da, overture_buildings_raster, target_crs)

        return composite_bldg_dem


def _combine_building_and_dem(dem, buildings, target_crs):
    coords_dict = {dim: dem.coords[dim].values for dim in dem.dims}

    # Convert to ndarray in order to mask and combine layers
    dem_nda = dem.to_numpy()
    bldg_nda = buildings.to_numpy().reshape(dem_nda.shape)

    # Mask of building cells
    mask = (bldg_nda != -9999) & (~np.isnan(bldg_nda))

    # Mask buildings onto DEM
    dem_nda[mask] = bldg_nda[mask]

    # Convert results into DataArray and re-add coordinates and CRS
    composite_xa = xr.DataArray(
        dem_nda,
        dims=["y", "x"],
        coords=coords_dict,
        name="elevation"
    )
    composite_xa.rio.write_crs(target_crs, inplace=True)

    return composite_xa


def _rasterize_polygons(gdf, values=["elevation"], snap_to_raster=None):
    """
    Rasterizes polygons in the GeoDataFrame to match the properties of a reference raster.

    Parameters:
        gdf (GeoDataFrame): The GeoDataFrame containing polygon geometries and values.
        values (list): List of column names whose values will be assigned to the raster.
                       Defaults to ["elevation"].
        snap_to_raster (xarray.DataArray): Reference raster for alignment (optional).

    Returns:
        xarray.DataArray: Rasterized version of the polygons with the specified values.
    """
    if gdf.empty:
        # Return an empty raster matching the reference raster if GeoDataFrame is empty
        feature_raster = xr.zeros_like(snap_to_raster)
        feature_raster.name = values[0] if values else "elevation"
        return feature_raster

    if snap_to_raster is None:
        raise ValueError("snap_to_raster must be provided for alignment.")

    # Extract raster properties from the reference raster
    transform = snap_to_raster.rio.transform()
    out_shape = (snap_to_raster.sizes["y"], snap_to_raster.sizes["x"])

    # Use `getattr` to safely access values when iterating through rows
    shapes = [
        (geometry, getattr(row, values[0])) for geometry, row in zip(gdf.geometry, gdf.itertuples())
    ]

    # Rasterize the polygons
    rasterized_array = rasterio.features.rasterize(
        shapes=shapes,
        out_shape=out_shape,
        transform=transform,
        fill=-9999,  # NoData value
        dtype="float32",
    )

    # Convert the rasterized array to an xarray.DataArray
    coords_dict = {dim: snap_to_raster.coords[dim].values for dim in snap_to_raster.dims}
    feature_raster = xr.DataArray(
        rasterized_array,
        dims=["y", "x"],
        coords=coords_dict,
        name=values[0] if values else "elevation"
    )
    feature_raster.rio.write_crs(snap_to_raster.rio.crs, inplace=True)

    return feature_raster