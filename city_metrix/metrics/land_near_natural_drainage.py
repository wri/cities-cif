import pandas as pd
import numpy as np
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import GeoZone, Metric
from city_metrix.layers import HeightAboveNearestDrainage, EsaWorldCover, EsaWorldCoverClass


class LandNearNaturalDrainage__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,  **kwargs):
        super().__init__(**kwargs)
        self.unit = 'percent'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:

        # neardrainage_area = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP).mask(HeightAboveNearestDrainage(thresh=1, nanval=np.nan)).groupby(geo_zone).count()
        # total_area = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP).groupby(geo_zone).count()
        neardrainage_area = HeightAboveNearestDrainage(thresh=1, nanval=np.nan).mask(EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)).groupby(geo_zone).count()
        total_area = HeightAboveNearestDrainage(thresh=0, nanval=0).mask(EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)).groupby(geo_zone).count()
        # total_area = HeightAboveNearestDrainage(nanval=0).groupby(geo_zone).count()

        if isinstance(neardrainage_area, pd.DataFrame):
            result = neardrainage_area.copy()
            result['value'] = 100 * (neardrainage_area['value'] / total_area['value'])
        else:
            result = 100 * (neardrainage_area / total_area)

        return result
