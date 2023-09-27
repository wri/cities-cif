from typing import List
from enum import Enum
import ee

from cities_indicators.city import City
from cities_indicators.indicators.built_land_without_tree_cover import BuiltLandWithTreeCover
from cities_indicators.indicators.surface_reflectivity import SurfaceReflectivity
from cities_indicators.indicators.tree_cover import TreeCover
from cities_indicators.indicators.tree_cover_gee import TreeCoverGEE
from cities_indicators.indicators.built_land_with_high_lst import BuiltUpHighLandSurfaceTemperature
from cities_indicators.indicators.built_land_with_high_lst_gee import BuiltUpHighLandSurfaceTemperatureGEE

class Indicator(Enum):
    BUILT_LAND_WITH_TREE_COVER = BuiltLandWithTreeCover
    SURFACE_REFLECTIVTY = SurfaceReflectivity
    TREE_COVER = TreeCover
    TREE_COVER_GEE = TreeCoverGEE
    BUILT_LAND_WITH_HIGH_LST = BuiltUpHighLandSurfaceTemperature
    BUILT_LAND_WITH_HIGH_LST_GEE = BuiltUpHighLandSurfaceTemperatureGEE


def get_indicators(cities: List[City], indicators: List[Indicator]):
    results = []

    # TODO need to pass admin level and union option
    for city in cities:
        for indicator in indicators:
            results.append(indicator.value().calculate(city))

    return results


def initialize_ee():
    _CREDENTIAL_FILE = 'gcsCIFcredential.json'
    GEE_SERVICE_ACCOUNT = 'developers@citiesindicators.iam.gserviceaccount.com'
    auth = ee.ServiceAccountCredentials(GEE_SERVICE_ACCOUNT, _CREDENTIAL_FILE)
    ee.Initialize(auth)
