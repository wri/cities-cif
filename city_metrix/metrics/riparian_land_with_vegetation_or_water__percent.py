import pandas as pd
from typing import Union
import geopandas as gpd
from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import RiparianAreas, NdwiSentinel2, FractionalVegetationPercent
from city_metrix.metrix_model import Metric, GeoZone

MIN_NDWI = 0.4
MIN_VEGETATION_PERCENT = 50

class RiparianLandWithVegetationOrWater__Percent(Metric):
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

        riparian_layer = RiparianAreas()
        water_layer = NdwiSentinel2(min_threshold=MIN_NDWI)
        vegetation_layer = FractionalVegetationPercent(min_threshold=MIN_VEGETATION_PERCENT)

        water_area = riparian_layer.mask(water_layer).groupby(geo_zone).count().fillna(0)
        vegetation_area = riparian_layer.mask(vegetation_layer).groupby(geo_zone).count().fillna(0)
        AND_area = vegetation_layer.mask(water_layer).groupby(geo_zone).count().fillna(0)
        OR_area = water_area + vegetation_area - and_area

        vegetationwater_fraction = OR_area / riparian_layer.groupby(geo_zone).count()
        
        if isinstance(vegetationwater_fraction, pd.DataFrame):
            result = vegetationwater_fraction.copy()
            result['value'] = vegetationwater_fraction['value'] * 100
        else:
            result = vegetationwater_fraction * 100

        return result
