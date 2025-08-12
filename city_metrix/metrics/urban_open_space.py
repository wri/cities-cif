import pandas as pd
from typing import Union
from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import EsaWorldCover, EsaWorldCoverClass, OpenStreetMap, OpenStreetMapClass
from city_metrix.metrix_model import Metric, GeoZone


class UrbanOpenSpace(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:

        built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
        open_space = OpenStreetMap(osm_class=OpenStreetMapClass.OPEN_SPACE)

        open_space_in_built_land = open_space.mask(built_up_land).groupby(geo_zone).count()
        built_land_counts = built_up_land.groupby(geo_zone).count()

        if not isinstance(open_space_in_built_land, (int, float)):
            open_space_in_built_land = open_space_in_built_land.fillna(0)

        if isinstance(open_space_in_built_land, pd.DataFrame):
            result = open_space_in_built_land.copy()
            result['value'] = open_space_in_built_land['value'] / built_land_counts['value']
        else:
            result = open_space_in_built_land / built_land_counts

        return result
