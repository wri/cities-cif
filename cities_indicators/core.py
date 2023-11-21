from typing import List, Tuple
from enum import Enum
import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
from google.oauth2 import service_account
import os
import ee
import os

from .city import City
from .indicators.built_land_without_tree_cover import BuiltLandWithTreeCover
from .indicators.surface_reflectivity import SurfaceReflectivity
from .indicators.tree_cover import TreeCover
from .indicators.tree_cover_gee import TreeCoverGEE
from .indicators.built_land_with_high_lst import BuiltUpHighLandSurfaceTemperature
from .indicators.built_land_with_high_lst_gee import BuiltUpHighLandSurfaceTemperatureGEE
from .indicators.non_tree_cover_by_land_use_gee import NonTreeCoverByLandUseGEE


class Indicator(Enum):
    BUILT_LAND_WITH_TREE_COVER = BuiltLandWithTreeCover
    SURFACE_REFLECTIVTY = SurfaceReflectivity
    TREE_COVER = TreeCover
    TREE_COVER_GEE = TreeCoverGEE
    BUILT_LAND_WITH_HIGH_LST = BuiltUpHighLandSurfaceTemperature
    BUILT_LAND_WITH_HIGH_LST_GEE = BuiltUpHighLandSurfaceTemperatureGEE
    NON_TREE_COVER_BY_LAND_USE_GEE = NonTreeCoverByLandUseGEE


def get_city_indicators(cities: List[Tuple[City, str]], indicators: List[Indicator]):
    results = []

    for city, admin_level in cities:
        for indicator in indicators:
            gdf = city.get_geom(admin_level)
            results.append(indicator.value().calculate(gdf))
    
    # Merge the list of GeoDataFrames into a single GeoDataFrame
    merged_gdf = gpd.GeoDataFrame(pd.concat(results, ignore_index=True))

    return merged_gdf


def get_indicators(gdf: GeoDataFrame, indicators: List[Indicator]):
    results = []

    # all analysis is done in WGS84
    reprojected_gdf = gdf.to_crs("4326").reset_index()

    for indicator in indicators:
        results.append(indicator.value().calculate(reprojected_gdf))

    # Merge the list of GeoDataFrames into a single GeoDataFrame
    merged_gdf = gpd.GeoDataFrame(pd.concat(results, ignore_index=True))

    return merged_gdf


def initialize_ee():
    _CREDENTIAL_FILE = 'gcsCIFcredential.json'
    GEE_SERVICE_ACCOUNT = 'developers@citiesindicators.iam.gserviceaccount.com'
    auth = ee.ServiceAccountCredentials(GEE_SERVICE_ACCOUNT, _CREDENTIAL_FILE)
    ee.Initialize(auth)
