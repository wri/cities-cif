from geopandas import GeoDataFrame, GeoSeries

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import Metric, GeoZone
from city_metrix.layers import (
    KeyBiodiversityAreas,
    ProtectedAreas,
    WorldPop
)

AWS_STEM = 'https://wri-cities-indicators.s3.us-east-1.amazonaws.com'
COUNTRYBBOXES_PATH = 'devdata/inputdata/country_bboxes.geojson'
COUNTRYBOUNDS_PATH = 'devdata/inputdata/country_boundaries.geojson'


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

        if self.country_code_iso3 is None:
            country_bboxes = GeoDataFrame.from_file(f'{AWS_STEM}/{COUNTRYBBOXES_PATH}')
            matches = country_bboxes.loc[country_bboxes.intersects(geo_zone.polygon)]
            if len(matches) > 1:
                country_bounds = GeoDataFrame.from_file(f'{AWS_STEM}/{COUNTRYBOUNDS_PATH}')
                matches = country_bounds.loc[country_bounds.intersects(geo_zone.polygon)]
            country_code_iso3 = matches.countrycode[matches.index[0]]
        else:
            country_code_iso3 = self.country_code_iso3

        worldpop_layer = WorldPop()
        kba_layer = KeyBiodiversityAreas(country_code_iso3)
        protected_layer = ProtectedAreas()

        kba_area = worldpop_layer.mask(kba_layer).groupby(geo_zone).count()
        protected_kba_area = worldpop_layer.mask(kba_layer).mask(protected_layer).groupby(geo_zone).count()

        return 100 * protected_kba_area / kba_area