import ee

from city_metrix.metrix_model import (Layer, get_image_collection, set_resampling_for_continuous_raster,
                                      validate_raster_resampling_method, GeoExtent)
from ..constants import GTIFF_FILE_EXTENSION, GeoType
from ..metrix_dao import write_layer
from ..repo_manager import retrieve_cached_city_data2

DEFAULT_SPATIAL_RESOLUTION = 30
DEFAULT_RESAMPLING_METHOD = 'bilinear'

class NasaDEM(Layer):
    GEOSPATIAL_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,  **kwargs):
        super().__init__(**kwargs)

    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
        resampling_method: interpolation method used by Google Earth Engine. Valid options: ('bilinear', 'bicubic', 'nearest').
    """
    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method:str=DEFAULT_RESAMPLING_METHOD, force_data_refresh=False):

        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)

        # Attempt to retrieve cached file based on layer_id.
        retrieved_cached_data, file_uri = retrieve_cached_city_data2(self, bbox, force_data_refresh)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        nasa_dem = ee.Image("NASA/NASADEM_HGT/001")

        ee_rectangle  = bbox.to_ee_rectangle()
        nasa_dem_elev = (ee.ImageCollection(nasa_dem)
                         .filterBounds(ee_rectangle['ee_geometry'])
                         .select('elevation')
                         .map(lambda x:
                              set_resampling_for_continuous_raster(x,
                                                                   resampling_method,
                                                                   spatial_resolution,
                                                                   ee_rectangle['crs']
                                                                   )
                              )
                         .mean()
                         )

        nasa_dem_elev_ic = ee.ImageCollection(nasa_dem_elev)
        data = get_image_collection(
            nasa_dem_elev_ic,
            ee_rectangle,
            spatial_resolution,
            "NASA DEM"
        ).elevation

        if bbox.geo_type == GeoType.CITY:
            write_layer(data, file_uri, self.GEOSPATIAL_FILE_FORMAT)

        return data
