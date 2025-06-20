from geopandas import GeoSeries

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import Metric, GeoZone
from city_metrix.layers import (
    KeyBiodiversityAreas,
    ProtectedAreas,
    WorldPop
)


class PercentKeyBiodiversityAreaProtected(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(
        self, country_code_iso3=None, **kwargs
    ):
        super().__init__(**kwargs)
        self.country_code_iso3 = country_code_iso3


    def get_metric(
        self, geo_zone: GeoZone, spatial_resolution: int = None
    ) -> GeoSeries:

        worldpop_layer = WorldPop()
        kba_layer = KeyBiodiversityAreas(self.country_code_iso3)
        protected_layer = ProtectedAreas()

        kba_area = worldpop_layer.mask(kba_layer).groupby(geo_zone).count()
        protected_kba_area = worldpop_layer.mask(kba_layer).mask(protected_layer).groupby(geo_zone).count()

        return 100 * protected_kba_area / kba_area