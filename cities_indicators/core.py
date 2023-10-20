from typing import List, Tuple
from enum import Enum
from geopandas import GeoDataFrame
import ee

from .city import City
from .indicators.built_land_without_tree_cover import BuiltLandWithTreeCover
from .indicators.surface_reflectivity import SurfaceReflectivity
from .indicators.tree_cover import TreeCover
from .indicators.tree_cover_gee import TreeCoverGEE
from .indicators.built_land_with_high_lst import BuiltUpHighLandSurfaceTemperature
from .indicators.built_land_with_high_lst_gee import BuiltUpHighLandSurfaceTemperatureGEE


class Indicator(Enum):
    BUILT_LAND_WITH_TREE_COVER = BuiltLandWithTreeCover
    SURFACE_REFLECTIVTY = SurfaceReflectivity
    TREE_COVER = TreeCover
    TREE_COVER_GEE = TreeCoverGEE
    BUILT_LAND_WITH_HIGH_LST = BuiltUpHighLandSurfaceTemperature
    BUILT_LAND_WITH_HIGH_LST_GEE = BuiltUpHighLandSurfaceTemperatureGEE


def get_city_indicators(cities: List[Tuple[City, str]], indicators: List[Indicator]):
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
