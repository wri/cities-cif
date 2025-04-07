from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import NaturalAreas
from city_metrix.metrics.metric import Metric


class NaturalAreasPercent(Metric):
    def __init__(self,  **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 zones: GeoDataFrame) -> GeoSeries:

        natural_areas = NaturalAreas().groupby(zones).mean()

        return natural_areas
