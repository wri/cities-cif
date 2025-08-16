import pandas as pd
from typing import Union
from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import Metric, GeoZone
from city_metrix.layers import TreeCanopyHeight, UrbanLandUse


MIN_TREE_HEIGHT = 3
ULU_INFORMAL_CLASS = 3

class PercentBuiltAreaWithoutTreeCover(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, height=MIN_TREE_HEIGHT, **kwargs):
        super().__init__(**kwargs)
        self.height = height

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:
        """
        Get percentage of land (assuming zones are based on urban extents)
        with no tree cover (>3 Global Canopy Height dataset).
        :param geo_zone: GeoDataFrame with geometries to collect zonal stats on
        :return: Pandas Series of percentages or DataFrame of value and zone
        """

        tree_canopy_height = TreeCanopyHeight(height=self.height)

        # informal_only: urban land use class 3 for Informal
        urban_land_use = UrbanLandUse(ulu_class=ULU_INFORMAL_CLASS)

        built_land = urban_land_use.groupby(geo_zone).count()
        built_land_with_tree_cover = urban_land_use.mask(tree_canopy_height).groupby(geo_zone).count()

        if not isinstance(built_land_with_tree_cover, (int, float)):
            built_land_with_tree_cover = built_land_with_tree_cover.fillna(0)

        if isinstance(built_land_with_tree_cover, pd.DataFrame):
            result = built_land_with_tree_cover.copy()
            result['value'] = 100 * (1 - (built_land_with_tree_cover['value'] / built_land['value']))
        else:
            result = 100 * (1 - (built_land_with_tree_cover / built_land))

        return result
