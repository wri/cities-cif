from typing import List
from enum import Enum

from cities_indicators.city import SupportedCity, City
from cities_indicators.indicators.built_land_without_tree_cover import BuiltLandWithTreeCover
from cities_indicators.indicators.surface_reflectivity import SurfaceReflectivity


class Indicator(Enum):
    BUILT_LAND_WITH_TREE_COVER = BuiltLandWithTreeCover
    SURFACE_REFLECTIVTY = SurfaceReflectivity


def get_indicators(cities: List[SupportedCity], indicators: List[Indicator]):
    results = []

    # TODO need to pass admin level and union option
    for city in cities:
        for indicator in indicators:
            results.append(indicator.value().calculate(City(city, admin_level=4)))

    return results

