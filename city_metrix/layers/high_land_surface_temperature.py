import datetime
import ee
import numpy as np
import xarray as xr

from .land_surface_temperature import LandSurfaceTemperature
from city_metrix.metrix_model import Layer, GeoExtent
from ..constants import GTIFF_FILE_EXTENSION, DEFAULT_DEVELOPMENT_ENV, CIF_CACHE_S3_BUCKET_URI

DEFAULT_SPATIAL_RESOLUTION = 30

class HighLandSurfaceTemperature(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["percentile", "num_seasons"]
    MINOR_NAMING_ATTS = None
    THRESHOLD_ADD = 3

    """
    Attributes:
        start_date: starting date for data retrieval
        end_date: ending date for data retrieval
    """
    def __init__(self, percentile=95, num_seasons=5, **kwargs):
        super().__init__(**kwargs)
        self.percentile = percentile
        self.num_seasons = num_seasons

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        lst_data = LandSurfaceTemperature(
            percentile=self.percentile,
            num_seasons=self.num_seasons,
            use_hot_window=True
            ).get_data(bbox)
        lst_mean = lst_data.mean(dim=['x', 'y'])
        high_lst = xr.where(lst_data >= (lst_mean + self.THRESHOLD_ADD), 1, np.nan)
        high_lst = high_lst.rio.write_crs(lst_data.crs)

        return high_lst

    