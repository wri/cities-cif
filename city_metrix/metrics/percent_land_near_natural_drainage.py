import pandas as pd
from typing import Union
import geopandas as gpd
from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import HeightAboveNearestDrainage
from city_metrix.metrix_model import GeoZone, Metric

DEFAULT_SPATIAL_RESOLUTION = 30

class LandNearNaturalDrainage__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,  **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:

        neardrainage_area = HeightAboveNearestDrainage(thresh=1, nanval=None).groupby(geo_zone).count()
        total_area = HeightAboveNearestDrainage(nanval=0).groupby(geo_zone).count()

        fraction_area = neardrainage_area / total_area

        isinstance(fraction_area, pd.DataFrame):
            result = fraction_area.copy()
            result['value'] = fraction_area['value'] * 100
        else:
            result = fraction_area * 100

        return result