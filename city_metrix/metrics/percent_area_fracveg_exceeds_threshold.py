import pandas as pd
from typing import Union
from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import Metric, GeoZone
from city_metrix.layers import FractionalVegetationPercent

class PercentAreaFracvegExceedsThreshold(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    CUSTOM_TILE_SIDE_M = 10000
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, min_threshold=60, year=2024, **kwargs):
        super().__init__(**kwargs)
        self.min_threshold = min_threshold
        self.year = year

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:
        fracveg_all_layer = FractionalVegetationPercent(min_threshold=None, year=self.year)
        fracveg_gte_thresh_layer = FractionalVegetationPercent(min_threshold=self.min_threshold, year=self.year)

        fracveg_gte_thresh_sum = fracveg_gte_thresh_layer.groupby(geo_zone,custom_tile_size_m=self.CUSTOM_TILE_SIDE_M).sum()
        fracveg_all_count = fracveg_all_layer.groupby(geo_zone,custom_tile_size_m=self.CUSTOM_TILE_SIDE_M).count()

        if isinstance(fracveg_gte_thresh_sum, pd.DataFrame):
            result = fracveg_gte_thresh_sum.copy()
            result['value'] = fracveg_gte_thresh_sum['value'] / fracveg_all_count['value']
        else:
            result = fracveg_gte_thresh_sum / fracveg_all_count

        return result