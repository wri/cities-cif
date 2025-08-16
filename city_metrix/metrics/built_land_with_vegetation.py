import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from geopandas import GeoDataFrame, GeoSeries
from city_metrix.layers import EsaWorldCoverClass, EsaWorldCover, FractionalVegetationPercent

class BuiltLandWithVegetation__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

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

        built_land = built_up_land.groupby(zones).count()
        vegetation_cover_in_built_land = FractionalVegetationPercent.mask(built_up_land).groupby(zones).count()

        fraction_vegetation_in_built_up_land = (vegetation_cover_in_built_land.fillna(0) / built_land)

        if isinstance(percent_vegetation_in_built_up_land, pd.DataFrame):
                result = percent_vegetation_in_built_up_land.copy()
                result['value'] = percent_vegetation_in_built_up_land['value']
        else:
            result = percent_vegetation_in_built_up_land

        return result
