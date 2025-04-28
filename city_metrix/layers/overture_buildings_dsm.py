import rasterio
import numpy as np
import xarray as xr
import rasterio.features
from exactextract import exact_extract

from city_metrix.metrix_model import Layer, GeoExtent, validate_raster_resampling_method
from city_metrix.ut_globus_city_handler.ut_globus_city_handler import search_for_ut_globus_city_by_contained_polygon
from . import NasaDEM
from ..constants import GTIFF_FILE_EXTENSION
from .overture_buildings_w_height import OvertureBuildingsHeight

DEFAULT_SPATIAL_RESOLUTION = 1
DEFAULT_RESAMPLING_METHOD = 'bilinear'

class OvertureBuildingsDSM(Layer):
    GEOSPATIAL_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        city: city id from https://sat-io.earthengine.app/view/ut-globus
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method:str=DEFAULT_RESAMPLING_METHOD):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)

        bbox_polygon = bbox.as_geographic_bbox().polygon
        ut_globus_city_name = search_for_ut_globus_city_by_contained_polygon(bbox_polygon)

        # Load the datasets
        buildings_gdf = OvertureBuildingsHeight(city=ut_globus_city_name).get_data(bbox)
        dem_da = NasaDEM().get_data(bbox, spatial_resolution=spatial_resolution, resampling_method=resampling_method)

        buildings_gdf['mode_elevation'] = (
            exact_extract(dem_da, buildings_gdf, ["mode"], output='pandas')['mode'])

        buildings_gdf["elevation_estimate"] = buildings_gdf["height"] + buildings_gdf["mode_elevation"]

        overture_buildings_raster = _rasterize_polygons(buildings_gdf, values=["elevation_estimate"],
                                                        snap_to_raster=dem_da)

        target_crs = dem_da.rio.crs
        composite_bldg_dem = _combine_building_and_dem(dem_da, overture_buildings_raster, target_crs)


        return composite_bldg_dem

def _combine_building_and_dem(dem, buildings, target_crs):
    coords_dict = {dim: dem.coords[dim].values for dim in dem.dims}

    # Convert to ndarray in order to mask and combine layers
    dem_nda = dem.to_numpy()
    bldg_nda = buildings.to_dataarray().to_numpy().reshape(dem_nda.shape)

    # Mask of building cells
    mask = (bldg_nda != -9999) & (~np.isnan(bldg_nda))

    # Mask buildings onto DEM
    dem_nda[mask] = bldg_nda[mask]

    #Convert results into DataArray and re-add coordinates and CRS
    composite_xa = xr.DataArray(dem_nda,
                      dims = ["y","x"],
                      coords = coords_dict
                      )
    composite_xa.rio.write_crs(target_crs, inplace=True)

    return composite_xa

def _rasterize_polygons(gdf, values=["Value"], snap_to_raster=None):
    from geocube.api.core import make_geocube
    if gdf.empty:
        feature_1m = xr.zeros_like(snap_to_raster)
    else:
        feature_1m = make_geocube(
            vector_data=gdf,
            measurements=values,
            like=snap_to_raster,
            # fill=0
        )

    return feature_1m
