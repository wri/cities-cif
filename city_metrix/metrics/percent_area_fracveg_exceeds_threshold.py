from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import FractionalVegetation
from city_metrix.metrics.metric import Metric

class PercentAreaFracvegExceedsThreshold(Metric):
    def __init__(self, min_threshold=0.6, year=2024, **kwargs):
        super().__init__(**kwargs)
        self.min_threshold = min_threshold
        self.year = year

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:
        fracveg_all_layer = FractionalVegetation(min_threshold=None, year=self.year)
        fracveg_gte_thresh_layer = FractionalVegetation(min_threshold=self.min_threshold, year=self.year)

        return fracveg_gte_thresh_layer.groupby(zones).sum() / fracveg_all_layer.groupby(zones).count()
