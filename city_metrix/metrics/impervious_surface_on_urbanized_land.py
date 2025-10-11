import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import GeoZone, Metric
from city_metrix.layers import UrbanExtents, ImperviousSurface, WorldPop


class ImperviousSurfaceOnUrbanizedLand__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, year=2015, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.unit = 'percent'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution=None) -> Union[pd.DataFrame | pd.Series]:

        impervious_layer = ImperviousSurface(year=self.year)
        urban_layer = UrbanExtents(year=self.year)
        area_layer = WorldPop()

        impervious_area = area_layer.mask(urban_layer).mask(impervious_layer).groupby(geo_zone).count()
        urban_area = area_layer.mask(urban_layer).groupby(geo_zone).count()

        if not isinstance(impervious_area, (int, float)):
            impervious_area = impervious_area.fillna(0)

        if isinstance(impervious_area, pd.DataFrame):
            result = impervious_area.copy()
            result['value'] = 100 * (impervious_area['value'] / urban_area['value'])
        else:
            result = 100 * (impervious_area / urban_area)

        return result
