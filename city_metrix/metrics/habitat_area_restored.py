import pandas as pd
import numpy as np
from typing import Union
from geocube.api.core import make_geocube

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import GeoExtent, GeoZone, Metric
from city_metrix.layers import LandCoverHabitatGlad, LandCoverHabitatChangeGlad


class HabitatAreaRestored__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["start_year", "end_year"]

    def __init__(self, start_year=2000, end_year=2020, **kwargs):
        super().__init__(**kwargs)
        self.start_year = start_year
        self.end_year = end_year
        self.unit = 'percent'
    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:

        orig_habitat = LandCoverHabitatGlad(year=self.start_year, return_value=1)
        orig_nonhabitat = LandCoverHabitatGlad(year=self.start_year, return_value=0)
        new_habitat = LandCoverHabitatGlad(year=self.end_year, return_value=1)

        orig_habitat_area = orig_habitat.groupby(geo_zone).count()
        orig_nonhabitat_area = orig_nonhabitat.groupby(geo_zone).count()
        new_habitat_area = new_habitat.groupby(geo_zone).count()

        if isinstance(orig_habitat_area, pd.DataFrame):
            result = orig_habitat_area.copy()
            result['value'] = round(100 * (new_habitat_area['value'] - orig_habitat_area['value']) / orig_nonhabitat_area['value'], 2)
        else:
            result = round(100 * (new_habitat_area - orig_habitat_area) / orig_nonhabitat_area, 2)

        return result
