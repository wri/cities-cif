import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import TreeCover
from city_metrix.metrix_model import Metric, GeoZone

class MeanTreeCover(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:
        """
        Get mean tree cover (WRI tropical tree cover).
        :param geo_zone: GeoZone with geometries to collect zonal stats on
        :return: Pandas Series of percentages or DataFrame of value and zone
        """
        mean_tree_cover = TreeCover().groupby(geo_zone).mean()

        if isinstance(mean_tree_cover, pd.DataFrame):
            result = mean_tree_cover.copy()
            result['value'] = mean_tree_cover['value'] / 100
        else:
            result = mean_tree_cover / 100

        return result
