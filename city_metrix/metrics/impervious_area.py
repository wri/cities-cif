import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import ImperviousSurface
from city_metrix.metrix_model import Metric, GeoZone


class ImperviousArea__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:
        imperv = ImperviousSurface()

        # monkey‐patch impervious get_data to fill na
        imperv_fillna = ImperviousSurface()
        imperv_fillna_get_data = imperv_fillna.get_data
        imperv_fillna.get_data = lambda bbox, spatial_resolution: imperv_fillna_get_data(bbox, spatial_resolution).fillna(0)

        # count with no NaNs
        imperv_count = imperv.groupby(geo_zone).count()
        # count all pixels
        imperv_fillna_count = imperv_fillna.groupby(geo_zone).count()

        if isinstance(imperv_count, pd.DataFrame):
            result = imperv_count.copy()
            result['value'] = 100 * (imperv_count['value'] / imperv_fillna_count['value'])
        else:
            result = 100 * (imperv_count / imperv_fillna_count)

        return result
