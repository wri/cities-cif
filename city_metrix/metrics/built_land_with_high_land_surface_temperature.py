from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import HighLandSurfaceTemperature, EsaWorldCoverClass, EsaWorldCover
from city_metrix.metrics.metric import Metric


class BuiltLandWithHighLST(Metric):
    def __init__(self,  **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:
        """
        Get percentage of built up land with low albedo based on Sentinel 2 imagery.
        :param zones:
        :return:
        """
        built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
        high_lst = HighLandSurfaceTemperature()

        built_land_counts = built_up_land.groupby(zones).count()
        built_high_lst_counts = high_lst.mask(built_up_land).groupby(zones).count()

        return built_high_lst_counts.fillna(0) / built_land_counts
