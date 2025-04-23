from pandas import GeoSeries

from city_metrix.constants import GEOJSON_FILE_EXTENSION
from city_metrix.layers import HighLandSurfaceTemperature, EsaWorldCoverClass, EsaWorldCover
from city_metrix.metrix_model import GeoZone, Metric


class BuiltLandWithHighLST(Metric):
    GEOSPATIAL_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,  **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:
        """
        Get percentage of built up land with low albedo based on Sentinel 2 imagery.
        :param geo_zone:
        :return:
        """
        built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
        high_lst = HighLandSurfaceTemperature()

        built_land_counts = (built_up_land
                             .groupby(geo_zone, force_data_refresh = False)
                             .count())
        built_high_lst_counts = (high_lst.mask(built_up_land)
                                 .groupby(geo_zone, force_data_refresh = False)
                                 .count())

        return built_high_lst_counts.fillna(0) / built_land_counts
