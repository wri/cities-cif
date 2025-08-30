import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import GeoZone, Metric
from city_metrix.layers import EsaWorldCoverClass, EsaWorldCover, FractionalVegetationPercent


class BuiltLandWithVegetation__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None
    CUSTOM_TILE_SIDE_M = 10000


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:
        """
        Get percentage of built up land (using ESA world cover) with NDVI vegetation cover.
        :param zones: GeoDataFrame with geometries to collect zonal stats on
        :return: Pandas Series of percentages
        """

        builtup_layer = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
        vegetation_layer = FractionalVegetationPercent(min_threshold=50)

        vegetation_cover_in_built_land = (builtup_layer.mask(vegetation_layer)
                                          .groupby(geo_zone, custom_tile_size_m=self.CUSTOM_TILE_SIDE_M).count())
        built_land = builtup_layer.groupby(geo_zone).count()

        if not isinstance(vegetation_cover_in_built_land, (int, float)):
            vegetation_cover_in_built_land = vegetation_cover_in_built_land.fillna(0)

        if isinstance(vegetation_cover_in_built_land, pd.DataFrame):
            result = vegetation_cover_in_built_land.copy()
            result['value'] = 100 * (vegetation_cover_in_built_land['value'] / built_land['value'])
        else:
            result = 100 * (vegetation_cover_in_built_land / built_land)

        return result
