from geopandas import GeoDataFrame, GeoSeries

from city_metrix.constants import GEOJSON_FILE_EXTENSION
from city_metrix.metrix_model import Metric
from city_metrix.layers import FractionalVegetation

class PercentAreaFracvegExceedsThreshold(Metric):
    GEOSPATIAL_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, min_threshold=0.6, year=2024, **kwargs):
        super().__init__(**kwargs)
        self.min_threshold = min_threshold
        self.year = year

    def get_metric(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:
        fracveg_all_layer = FractionalVegetation(min_threshold=None, year=self.year)
        fracveg_gte_thresh_layer = FractionalVegetation(min_threshold=self.min_threshold, year=self.year)

        return fracveg_gte_thresh_layer.groupby(zones).sum() / fracveg_all_layer.groupby(zones).count()
