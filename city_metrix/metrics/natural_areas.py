import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import NaturalAreas
from city_metrix.metrix_model import GeoZone, Metric


class NaturalAreas__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,  **kwargs):
        super().__init__(**kwargs)
        self.unit = 'percent'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:

        natural_areas = NaturalAreas().groupby(geo_zone).mean()

        if isinstance(natural_areas, pd.DataFrame):
            result = natural_areas.copy()
            result['value'] = natural_areas['value'] * 100
        else:
            result = natural_areas * 100

        return result
