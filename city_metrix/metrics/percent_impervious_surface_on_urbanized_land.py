import pandas as pd
from typing import Union
from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import GeoZone, Metric
from city_metrix.layers import UrbanExtents, ImperviousSurface, WorldPop


DEFAULT_SPATIAL_RESOLUTION = 100

class PercentImperviousSurfaceOnUrbanizedLand(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution=DEFAULT_SPATIAL_RESOLUTION) -> Union[pd.DataFrame | pd.Series]:

        impervious_layer = ImperviousSurface()
        urban_layer = UrbanExtents()
        area_layer = WorldPop()
        fraction = area_layer.mask(urban_layer).mask(impervious_layer).groupby(geo_zone).count() / area_layer.mask(urban_layer).groupby(geo_zone).count()
        if isinstance(fraction, pd.DataFrame):
            result = fraction.copy()
            result['value'] = fraction['value'] * 100
        else:
            result = result * 100
        return result
