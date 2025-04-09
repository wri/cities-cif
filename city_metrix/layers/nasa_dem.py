import ee

from .layer import Layer, get_image_collection, set_resampling_for_continuous_raster, validate_raster_resampling_method
from city_metrix.metrix_dao import retrieve_cached_city_data
from .layer_geometry import GeoExtent
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 30
DEFAULT_RESAMPLING_METHOD = 'bilinear'

class NasaDEM(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_LAYER_NAMING_ATTS = None
    MINOR_LAYER_NAMING_ATTS = None

    def __init__(self,  **kwargs):
        super().__init__(**kwargs)

    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
        resampling_method: interpolation method used by Google Earth Engine. Valid options: ('bilinear', 'bicubic', 'nearest').
    """
    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method:str=DEFAULT_RESAMPLING_METHOD, allow_cache_retrieval=False):

        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)

        # Attempt to retrieve cached file based on layer_id.
        retrieved_cached_data = retrieve_cached_city_data(self, bbox, allow_cache_retrieval)
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

        return data
