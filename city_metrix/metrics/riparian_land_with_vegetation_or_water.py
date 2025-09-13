import pandas as pd
from typing import Union

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
        self.unit = 'percent'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        """
        Get total area as number of pixels in NwdiSentinel2.
        Get water area as number of 1-valued pixels in SurfaceWater.
        :param geo_zone: GeoZone with geometries to collect zonal stats on
        :return: Pandas Series of percentages
        """

        riparian_layer = RiparianAreas()
        water_layer = NdwiSentinel2(min_threshold=MIN_NDWI)
        vegetation_layer = FractionalVegetationPercent(min_threshold=MIN_VEGETATION_PERCENT)

        riparian_area = riparian_layer.groupby(geo_zone).count()
        water_area = riparian_layer.mask(water_layer).groupby(geo_zone).count().fillna(0)
        vegetation_area = riparian_layer.mask(vegetation_layer).groupby(geo_zone).count().fillna(0)

        AND_area = vegetation_layer.mask(water_layer).groupby(geo_zone).count().fillna(0)
        OR_area = water_area + vegetation_area - AND_area

        if not isinstance(OR_area, (int, float)):
            OR_area = OR_area.fillna(0)

        if isinstance(riparian_area, pd.DataFrame):
            result = riparian_area.copy()
            result['value'] = 100 * (OR_area['value'] / riparian_area['value'])
        else:
            result = 100 * (OR_area / riparian_area)

        return result
