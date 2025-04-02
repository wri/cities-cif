import ee
from xrspatial import slope

from .layer import Layer, validate_raster_resampling_method
from .nasa_dem import NasaDEM
from .layer_dao import retrieve_cached_city_data
from .layer_geometry import GeoExtent

DEFAULT_SPATIAL_RESOLUTION = 30
DEFAULT_RESAMPLING_METHOD = 'bilinear'

class HighSlope(Layer):
    OUTPUT_FILE_FORMAT = 'tif'
    MAJOR_LAYER_NAMING_ATTS = ["slope_threshold"]
    MINOR_LAYER_NAMING_ATTS = None

    """
    Attributes:
        slope_threshold
    """
    def __init__(self, slope_threshold:int=10, **kwargs):
        super().__init__(**kwargs)
        self.slope_threshold = slope_threshold

    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
        resampling_method: interpolation method used by Google Earth Engine. Valid options: ('bilinear', 'bicubic', 'nearest').
    """
    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method: str = DEFAULT_RESAMPLING_METHOD, allow_s3_cache_retrieval=False):

        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)

        # Attempt to retrieve cached file based on layer_id.
        retrieved_cached_data = retrieve_cached_city_data(self, bbox, allow_s3_cache_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        nasa_dem = NasaDEM().get_data(bbox, spatial_resolution=spatial_resolution,
                                      resampling_method=resampling_method)

        slope_data = slope(nasa_dem)
        # filter for steep slope
        data = slope_data.where(slope_data >= self.slope_threshold)

        return data
