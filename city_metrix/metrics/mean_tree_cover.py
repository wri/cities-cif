import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import TreeCanopyHeight
from city_metrix.metrix_model import Metric, GeoZone

DEFAULT_SPATIAL_RESOLUTION = 10


class MeanTreeCover__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:
        """
        Get mean tree cover (WRI-Meta Global Canopy Height Dataset).
        :param geo_zone: GeoZone with geometries to collect zonal stats on
        :return: Pandas Series of percentages or DataFrame of value and zone
        """
        
        tree_cover_area = TreeCanopyHeight(height=MIN_CANOPY_HEIGHT, spatial_resolution=DEFAULT_SPATIAL_RESOLUTION).groupby(geo_zone).count()
        total_area = TreeCanopyHeight(height=0, spatial_resolution=DEFAULT_SPATIAL_RESOLUTION).groupby(geo_zone).count()

        if isinstance(tree_cover_area, pd.DataFrame):
            result = tree_cover_area.copy()
            result['value'] = tree_cover_area['value'] / total_area['value']
        else:
            result = tree_cover_area / total_area

        return result
