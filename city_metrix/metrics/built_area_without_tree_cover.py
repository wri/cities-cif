import pandas as pd
from typing import Union
import datetime
from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import Metric, GeoZone
from city_metrix.layers import TreeCanopyHeight, EsaWorldCover, EsaWorldCoverClass

MIN_TREE_HEIGHT = 3


class BuiltAreaWithoutTreeCover__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["height", "year"]

    def __init__(self, height=MIN_TREE_HEIGHT, year=2025, **kwargs):
        super().__init__(**kwargs)
        self.height = height
        self.year = year
        self.unit = 'percent'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        """
        Get percentage of land (assuming zones are based on urban extents)
        with no tree cover (>3 Global Canopy Height dataset).
        :param geo_zone: GeoDataFrame with geometries to collect zonal stats on
        :return: Pandas Series of percentages or DataFrame of value and zone
        """

        tree_canopy_height = TreeCanopyHeight(height=self.height)

        built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)

        built_land_count = built_up_land.groupby(geo_zone).count()
        built_land_with_tree_cover_count = built_up_land.mask(tree_canopy_height).groupby(geo_zone).count()

        if not isinstance(built_land_with_tree_cover_count, (int, float)):
            built_land_with_tree_cover_count = built_land_with_tree_cover_count.fillna(0)

        if isinstance(built_land_with_tree_cover_count, pd.DataFrame):
            result = built_land_with_tree_cover_count.copy()
            result['value'] = 100 * (1 - (built_land_with_tree_cover_count['value'] / built_land_count['value']))
        else:
            result = 100 * (1 - (built_land_with_tree_cover_count / built_land_count))

        return result
