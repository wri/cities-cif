from typing import List
from enum import Enum
import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
from google.oauth2 import service_account
import ee
import os

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


def get_city_indicators(cities: List[tuple[City, str]], indicators: List[Indicator]):
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

    for indicator in indicators:
        results.append(indicator.value().calculate(gdf))

    # Merge the list of GeoDataFrames into a single GeoDataFrame
    merged_gdf = gpd.GeoDataFrame(pd.concat(results, ignore_index=True))

    return merged_gdf


def initialize_ee():
    _CREDENTIAL_FILE = 'gcsCIFcredential.json'
    credentials = service_account.Credentials.from_service_account_file(_CREDENTIAL_FILE)
    # GEE_SERVICE_ACCOUNT = 'developers@citiesindicators.iam.gserviceaccount.com'
    auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
    ee.Initialize(auth)
