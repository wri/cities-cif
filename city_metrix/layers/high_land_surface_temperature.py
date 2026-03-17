import datetime

import ee

from city_metrix.metrix_model import GeoExtent, Layer
from city_metrix.metrix_tools import align_raster_array

from ..constants import GTIFF_FILE_EXTENSION
from .land_surface_temperature import LandSurfaceTemperature
from .world_pop import WorldPop

DEFAULT_SPATIAL_RESOLUTION_LANDSAT = 30
DEFAULT_SPATIAL_RESOLUTION_MODIS = 1000
HOT_SEASON_LENGTH = 90

class HighLandSurfaceTemperature(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None
    THRESHOLD_ADD = 3

    """
    Attributes:
        start_date: starting date for data retrieval
        end_date: ending date for data retrieval
    """
    def __init__(self, start_date="2023-01-01", end_date="2026-01-01", index_aggregation=False, high_lst=False, use_modis=False, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.index_aggregation = index_aggregation
        self.high_lst = high_lst
        self.use_modis = use_modis

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        # spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        spatial_resolution = self.resolution or spatial_resolution or [DEFAULT_SPATIAL_RESOLUTION_LANDSAT, DEFAULT_SPATIAL_RESOLUTION_MODIS][int(self.use_modis)]
   
        geographic_bbox = bbox.as_geographic_bbox()

        
        lst = (LandSurfaceTemperature(self.start_date, self.end_date, hot_season_length=HOT_SEASON_LENGTH, use_modis=self.use_modis)
               .get_data(bbox=geographic_bbox, spatial_resolution=spatial_resolution))

        if self.high_lst:
            lst_mean = lst.mean(dim=['x', 'y'])
            lst_array = lst.where(lst >= (lst_mean + self.THRESHOLD_ADD))
        else:
            lst_array = lst
        if self.index_aggregation:
            wp_array =  WorldPop().get_data(bbox)
            lst_array = align_raster_array(lst_array, wp_array)
        return lst_array
