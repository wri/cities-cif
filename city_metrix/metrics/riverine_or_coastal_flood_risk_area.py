import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import AqueductFlood
from city_metrix.metrix_model import GeoZone, Metric

INUNDATION_THRESHOLD = 1


class RiverineOrCoastalFloodRiskArea__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["year"]

    def __init__(self,  year=2050, **kwargs):
        super().__init__(**kwargs)
        self.year = year # [1980, 2030, 2050, 2080]
        self.unit = 'percent'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:

        floodrisk_layer = AqueductFlood(report_threshold=INUNDATION_THRESHOLD, year=self.year)
        totalarea_layer = AqueductFlood(report_threshold=None, year=self.year)

        floodrisk_count = floodrisk_layer.groupby(geo_zone).count()
        totalarea_count = totalarea_layer.groupby(geo_zone).count()

        if not isinstance(floodrisk_count, (int, float)):
            floodrisk_count = floodrisk_count.fillna(0)

        if isinstance(floodrisk_count, pd.DataFrame):
            result = floodrisk_count.copy()
            result['value'] = (floodrisk_count['value'] / totalarea_count['value']) * 100
        else:
            result = (floodrisk_count / totalarea_count) * 100

        return result
