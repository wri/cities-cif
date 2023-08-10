from typing import List
from enum import Enum
import ee
import os

from cities_indicators.city import City
from cities_indicators.indicators.built_land_without_tree_cover import BuiltLandWithTreeCover
from cities_indicators.indicators.surface_reflectivity import SurfaceReflectivity
from cities_indicators.indicators.tree_cover import TreeCover
from cities_indicators.indicators.tree_cover_gee import TreeCoverGEE

class Indicator(Enum):
    BUILT_LAND_WITH_TREE_COVER = BuiltLandWithTreeCover
    SURFACE_REFLECTIVTY = SurfaceReflectivity
    TREE_COVER = TreeCover
    TREE_COVER_GEE = TreeCoverGEE


def get_indicators(cities: List[City], indicators: List[Indicator]):
    results = []

    # TODO need to pass admin level and union option
    for city in cities:
        for indicator in indicators:
            results.append(indicator.value().calculate(city))

    return results


def initialize_ee():
    # get GEE credentials from env file
    GEE_JSON = os.environ.get("GEE_JSON")
    _CREDENTIAL_FILE = 'credentials.json'
    GEE_SERVICE_ACCOUNT = os.environ.get("GEE_SERVICE_ACCOUNT")
    with open(_CREDENTIAL_FILE, 'w') as f:
        f.write(GEE_JSON)
    auth = ee.ServiceAccountCredentials(GEE_SERVICE_ACCOUNT, _CREDENTIAL_FILE)
    ee.Initialize(auth)
