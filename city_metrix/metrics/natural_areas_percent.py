from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import NaturalAreas
from city_metrix.metrics import GeoZone
from city_metrix.metrics.metric import Metric


class NaturalAreasPercent(Metric):
    def __init__(self,  **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:

        natural_areas = 100 * NaturalAreas().groupby(geo_zone).mean()

        return natural_areas
