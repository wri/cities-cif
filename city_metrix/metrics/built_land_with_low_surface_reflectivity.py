from geopandas import GeoSeries

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import Albedo, EsaWorldCoverClass, EsaWorldCover
from city_metrix.metrix_model import GeoZone, Metric


class BuiltLandWithLowSurfaceReflectivity(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,
                 start_date="2021-01-01",
                 end_date="2022-01-01",
                 albedo_threshold=0.2,
                 **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.albedo_threshold = albedo_threshold

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:
        """
        Get percentage of built up land with low albedo based on Sentinel 2 imagery.
        :param geo_zone: GeoDataFrame with geometries to collect zonal stats over
        :param start_date: start time for collecting albedo values.
        :param end_date: end time for collecting albedo values.
        :param albedo_threshold: threshold for "low" albedo.
        :return: Pandas Series of percentages
        """
        built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
        albedo = Albedo(start_date=self.start_date, end_date=self.end_date, threshold=self.albedo_threshold)

        built_land_counts = built_up_land.groupby(geo_zone).count()
        built_albedo_counts = albedo.mask(built_up_land).groupby(geo_zone).count()

        return built_albedo_counts / built_land_counts
