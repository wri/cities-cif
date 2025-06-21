from geopandas import GeoSeries

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import NdwiSentinel2, SurfaceWater
from city_metrix.metrix_model import Metric, GeoZone

class PercentWaterCover(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, year=2024, **kwargs):
        super().__init__(**kwargs)
        self.year = year

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:
        """
        Get total area as number of pixels in NwdiSentinel2.
        Get water area as number of 1-valued pixels in SurfaceWater.
        :param geo_zone: GeoZone with geometries to collect zonal stats on
        :return: Pandas Series of percentages
        """

        total_area_layer = NdwiSentinel2(year=self.year)
        water_layer = SurfaceWater(year=self.year)
        return 100 * water_layer.groupby(geo_zone).count().fillna(0) / total_area_layer.groupby(geo_zone).count()
