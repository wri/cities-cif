import pandas as pd
import geopandas as gpd
from typing import Union, Optional

from city_metrix.constants import CSV_FILE_EXTENSION, WGS_CRS
from city_metrix.metrix_model import Metric, GeoZone
from city_metrix.layers import (
    KeyBiodiversityAreas,
    EsaWorldCover,
    EsaWorldCoverClass,
    ProtectedAreas,
    WorldPop,
)

AWS_STEM = 'https://wri-cities-indicators.s3.us-east-1.amazonaws.com'
COUNTRYBBOXES_PATH = 'devdata/inputdata/country_bboxes.geojson'
COUNTRYBOUNDS_PATH = 'devdata/inputdata/country_boundaries.geojson'


def _to_geographic(poly, source_crs):
    gdf = gpd.GeoDataFrame({'id': [0], 'geometry': [poly]}, crs=source_crs).to_crs(WGS_CRS)
    return gdf.geometry.iloc[0]

def _resolve_country_iso3(geo_zone: GeoZone, country_code_iso3: Optional[str]) -> str:
    if country_code_iso3:
        return country_code_iso3

    country_bboxes = gpd.read_file(f'{AWS_STEM}/{COUNTRYBBOXES_PATH}')
    geo_polygon = _to_geographic(geo_zone.polygon, geo_zone.crs)
    matches = country_bboxes.loc[country_bboxes.intersects(geo_polygon)]
    if len(matches) > 1:
        country_bounds = gpd.read_file(f'{AWS_STEM}/{COUNTRYBOUNDS_PATH}')
        matches = country_bounds.loc[country_bounds.intersects(geo_polygon)]
    if matches.empty:
        raise ValueError(
            "Could not resolve country code from the provided GeoZone.")
    return matches.countrycode.iloc[0]


class KeyBiodiversityAreaProtected__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, country_code_iso3=None, **kwargs):
        super().__init__(**kwargs)
        self.country_code_iso3 = country_code_iso3

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame, pd.Series]:
        country_code_iso3 = _resolve_country_iso3(geo_zone, self.country_code_iso3)

        worldpop_layer = WorldPop()
        kba_layer = KeyBiodiversityAreas(country_code_iso3)
        protected_layer = ProtectedAreas()

        kba_area = worldpop_layer.mask(kba_layer).groupby(geo_zone).count()
        protected_kba_area = worldpop_layer.mask(kba_layer).mask(protected_layer).groupby(geo_zone).count().fillna(0)

        if isinstance(kba_area, pd.DataFrame):
            result = kba_area.copy()
            result['value'] = 100 * (protected_kba_area['value'] / kba_area['value'])
        else:
            result = 100 * protected_kba_area / kba_area

        result = 100 * protected_kba_area / kba_area

        return result


class KeyBiodiversityAreaUndeveloped__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, country_code_iso3=None, **kwargs):
        super().__init__(**kwargs)
        self.country_code_iso3 = country_code_iso3

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame, pd.Series]:
        country_code_iso3 = _resolve_country_iso3(geo_zone, self.country_code_iso3)

        worldpop_layer = WorldPop()
        kba_layer = KeyBiodiversityAreas(country_code_iso3)
        builtup_layer = EsaWorldCover(EsaWorldCoverClass.BUILT_UP)

        kba_area = worldpop_layer.mask(kba_layer).groupby(geo_zone).count()
        builtup_kba_area = worldpop_layer.mask(kba_layer).mask(builtup_layer).groupby(geo_zone).count().fillna(0)

        if isinstance(kba_area, pd.DataFrame):
            result = kba_area.copy()
            result['value'] = 100 * (1 - (builtup_kba_area['value'] / kba_area['value']))
        else:
            result = 100 * (1 - (builtup_kba_area / kba_area))

        return result