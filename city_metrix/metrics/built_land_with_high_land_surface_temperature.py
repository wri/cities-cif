import pandas as pd
from typing import Union
from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import HighLandSurfaceTemperature, EsaWorldCoverClass, EsaWorldCover
from city_metrix.metrix_model import GeoZone, Metric


class BuiltLandWithHighLST(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,  **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:
        """
        Get percentage of built up land with low albedo based on Sentinel 2 imagery.
        :param geo_zone: GeoDataFrame with geometries to collect zonal stats over
        :return: Pandas Series of percentages or DataFrame of value and zone
        """
        built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
        high_lst = HighLandSurfaceTemperature()

        built_land_counts = (built_up_land
                             .groupby(geo_zone, force_data_refresh = False)
                             .count())
        built_high_lst_counts = (high_lst.mask(built_up_land)
                                 .groupby(geo_zone, force_data_refresh = False)
                                 .count())

        if not isinstance(built_high_lst_counts, (int, float)):
            built_high_lst_counts = built_high_lst_counts.fillna(0)

        if isinstance(built_high_lst_counts, pd.DataFrame):
            result = built_high_lst_counts.copy()
            result['value'] = built_high_lst_counts['value'] / built_land_counts['value']
        else:
            result = built_high_lst_counts / built_land_counts

        return result
