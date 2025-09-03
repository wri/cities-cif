import pandas as pd
from typing import Union
from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import ProtectedAreas, EsaWorldCover
from city_metrix.metrix_model import Metric, GeoZone


class ProtectedArea__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,
                 status=['Inscribed', 'Adopted', 'Designated', 'Established'],
                 status_year=2024,
                 iucn_cat=['Ia', 'Ib', 'II', 'III', 'IV', 'V', 'VI', 'Not Applicable', 'Not Assigned', 'Not Reported'],
                 **kwargs):
        super().__init__(**kwargs)
        self.status = status
        self.status_year = status_year
        self.iucn_cat = iucn_cat

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:

        world_cover = EsaWorldCover(year=2021)
        protect_area = ProtectedAreas(status=self.status, status_year=self.status_year, iucn_cat=self.iucn_cat)

        protect_area_in_world_cover = world_cover.mask(protect_area).groupby(geo_zone).count()
        world_cover_counts = world_cover.groupby(geo_zone).count()

        if not isinstance(protect_area_in_world_cover, (int, float)):
            protect_area_in_world_cover = protect_area_in_world_cover.fillna(0)

        if isinstance(protect_area_in_world_cover, pd.DataFrame):
            result = protect_area_in_world_cover.copy()
            result['value'] = 100 * (protect_area_in_world_cover['value'] / world_cover_counts['value'])
        else:
            result = 100 * protect_area_in_world_cover / world_cover_counts

        return result

