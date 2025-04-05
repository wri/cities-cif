from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import TreeCover, EsaWorldCoverClass, EsaWorldCover
from city_metrix.metrics.metric import Metric

class MeanTreeCover(Metric):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 zones: GeoDataFrame) -> GeoSeries:
        """
        Get mean tree cover (WRI tropical tree cover).
        :param zones: GeoDataFrame with geometries to collect zonal stats on
        :return: Pandas Series of percentages
        """
        return TreeCover().groupby(zones).mean().divide(100)
