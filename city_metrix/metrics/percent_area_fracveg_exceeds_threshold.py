from geopandas import GeoSeries

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import Metric, GeoZone
from city_metrix.layers import FractionalVegetation

class PercentAreaFracvegExceedsThreshold(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, min_threshold=60, year=2024, **kwargs):
        super().__init__(**kwargs)
        self.min_threshold = min_threshold
        self.year = year

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:
        fracveg_all_layer = FractionalVegetation(min_threshold=None, year=self.year)
        fracveg_gte_thresh_layer = FractionalVegetation(min_threshold=self.min_threshold, year=self.year)

        return fracveg_gte_thresh_layer.groupby(geo_zone).sum() / fracveg_all_layer.groupby(geo_zone).count()
