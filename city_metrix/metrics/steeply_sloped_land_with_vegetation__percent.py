import pandas as pd
from typing import Union
import geopandas as gpd
from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import Slope, FractionalVegetationPercent
from city_metrix.metrix_model import Metric, GeoZone

MIN_SLOPE_DEGREES = 10
MIN_VEGETATION_PERCENT = 60

class SteeplySlopedLandWithVegetation__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, year=2024, **kwargs):
        super().__init__(**kwargs)
        self.year = year

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:
        """
        Get total area as number of pixels in NwdiSentinel2.
        Get water area as number of 1-valued pixels in SurfaceWater.
        :param geo_zone: GeoZone with geometries to collect zonal stats on
        :return: Pandas Series of percentages
        """

        steep_layer = Slope(min_threshold=MIN_SLOPE_DEGREES)
        vegetation_layer = FractionalVegetationPercent(min_threshold=MIN_VEGETATION_PERCENT)

        vegetation_fraction = steep_layer.mask(vegetation_layer).groupby(geo_zone).count().fillna(0) / steep_layer.groupby(geo_zone).count()
        
        if isinstance(vegetation_fraction, pd.DataFrame):
            result = vegetation_fraction.copy()
            result['value'] = vegetation_fraction['value'] * 100
        else:
            result = vegetation_fraction * 100

        return result
