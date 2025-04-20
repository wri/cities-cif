from xrspatial import slope

from city_metrix.metrix_model import Layer, validate_raster_resampling_method, GeoExtent
from .nasa_dem import NasaDEM
from ..constants import GTIFF_FILE_EXTENSION, GeoType
from ..metrix_dao import write_layer
from ..repo_manager import retrieve_cached_city_data2

DEFAULT_SPATIAL_RESOLUTION = 30
DEFAULT_RESAMPLING_METHOD = 'bilinear'

class HighSlope(Layer):
    GEOSPATIAL_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["slope_threshold"]
    MINOR_NAMING_ATTS = None

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
                 resampling_method: str = DEFAULT_RESAMPLING_METHOD, force_data_refresh=False):

        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)

        # Attempt to retrieve cached file based on layer_id.
        retrieved_cached_data, file_uri = retrieve_cached_city_data2(self, bbox, force_data_refresh)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        nasa_dem = NasaDEM().get_data(bbox, spatial_resolution=spatial_resolution,
                                      resampling_method=resampling_method)

        slope_data = slope(nasa_dem)
        # filter for steep slope
        data = slope_data.where(slope_data >= self.slope_threshold)

        if bbox.geo_type == GeoType.CITY:
            write_layer(high_lst, file_uri, self.GEOSPATIAL_FILE_FORMAT)

        return data
