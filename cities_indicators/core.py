from typing import List
from enum import Enum
from geopandas import GeoDataFrame
import ee

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


def get_city_indicators(cities: List[tuple[City, str]], indicators: List[Indicator]):
    results = []

    for city, admin_level in cities:
        for indicator in indicators:
            gdf = city.get_geom(admin_level)
            results.append(indicator.value().calculate(gdf))

    return results


def get_indicators(gdf: GeoDataFrame, indicators: List[Indicator]):
    results = []

    for indicator in indicators:
        results.append(indicator.value().calculate(gdf))

    return results


def initialize_ee():
    _CREDENTIAL_FILE = 'gcsCIFcredential.json'
    GEE_SERVICE_ACCOUNT = 'developers@citiesindicators.iam.gserviceaccount.com'
    auth = ee.ServiceAccountCredentials(GEE_SERVICE_ACCOUNT, _CREDENTIAL_FILE)
    ee.Initialize(auth)
