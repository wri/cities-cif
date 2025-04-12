from geopandas import GeoDataFrame, GeoSeries

from city_metrix.metrics.metric_geometry import GeoZone
from city_metrix.layers import TreeCover, EsaWorldCoverClass, EsaWorldCover
from city_metrix.metrics.metric import Metric

class MeanTreeCover(Metric):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:
        """
        Get mean tree cover (WRI tropical tree cover).
        :param geo_zone: GeoZone with geometries to collect zonal stats on
        :return: Pandas Series of percentages
        """
        return TreeCover().groupby(geo_zone).mean().divide(100)
