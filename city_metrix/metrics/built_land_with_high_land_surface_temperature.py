import pandas as pd
from typing import Union
import datetime
from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import GeoZone, Metric
from city_metrix.layers import HighLandSurfaceTemperature, EsaWorldCoverClass, EsaWorldCover


class BuiltLandWithHighLST__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["year"]

    def __init__(self, year=datetime.datetime.now().year,  **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.unit = 'percent'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        """
        Get percentage of built up land with low albedo based on Sentinel 2 imagery.
        :param geo_zone: GeoDataFrame with geometries to collect zonal stats over
        :return: Pandas Series of percentages or DataFrame of value and zone
        """
        built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
        high_lst = HighLandSurfaceTemperature()

        built_land_counts = (built_up_land
                             .groupby(geo_zone)
                             .count())
        built_high_lst_counts = (built_up_land.mask(high_lst)
                                 .groupby(geo_zone)
                                 .count())


        if not isinstance(built_high_lst_counts, (int, float)):
            built_high_lst_counts = built_high_lst_counts.fillna(0)

        if isinstance(built_high_lst_counts, pd.DataFrame):
            result = built_high_lst_counts.copy()
            result['value'] = 100 * built_high_lst_counts['value'] / built_land_counts['value']
        else:
            result = 100 * built_high_lst_counts / built_land_counts

        return result
