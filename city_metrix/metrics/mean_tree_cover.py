import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import Metric, GeoZone
from city_metrix.layers import TreeCanopyHeight, EsaWorldCover

MIN_TREE_HEIGHT = 3 # meters

class MeanTreeCover__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["year"]

    def __init__(self, year=2025, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.unit = 'percent'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        """
        Get mean tree cover (Meta-WRI Tree Canopy Height >= 3m).
        :param geo_zone: GeoZone with geometries to collect zonal stats on
        :return: Pandas Series of percentages or DataFrame of value and zone
        """

        trees_greaterthan_0m = TreeCanopyHeight(height=0)
        total_area = trees_greaterthan_0m.groupby(geo_zone).count()
        
        trees_greaterthan_3m = TreeCanopyHeight(height=MIN_TREE_HEIGHT)
        tree_area = anything.mask(trees_greaterthan_3m).groupby(geo_zone).count()

        if isinstance(total_area, pd.DataFrame):
            result = total_area.copy()
            result['value'] = 100 * tree_area['value'] / total_area['value']
        else:
            result = 100 * tree_area / total_area

        return result
