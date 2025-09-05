import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import NdwiSentinel2, SurfaceWater
from city_metrix.metrix_model import Metric, GeoZone


class WaterCover__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, year=2024, **kwargs):
        super().__init__(**kwargs)
        self.year = year

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        """
        Get total area as number of pixels in NwdiSentinel2.
        Get water area as number of 1-valued pixels in SurfaceWater.
        :param geo_zone: GeoZone with geometries to collect zonal stats on
        :return: Pandas Series of percentages
        """
        water_layer = SurfaceWater(year=self.year)
        total_area_layer = NdwiSentinel2(year=self.year)

        water_area = water_layer.groupby(geo_zone).count()
        total_area = total_area_layer.groupby(geo_zone).count()

        if not isinstance(water_area, (int, float)):
            water_area = water_area.fillna(0)

        if isinstance(water_area, pd.DataFrame):
            result = water_area.copy()
            result['value'] = (water_area['value'] / total_area['value']) * 100
        else:
            result = (water_area / total_area) * 100

        return result
