from typing import List
from enum import Enum

from cities_indicators.city import SupportedCity, City
from cities_indicators.indicators.built_land_without_tree_cover import BuiltLandWithTreeCover


class Indicator(Enum):
    BUILT_LAND_WITH_TREE_COVER = BuiltLandWithTreeCover


def get_indicators(cities: List[SupportedCity], indicators: List[Indicator]):
    results = []
    for city in cities:
        for indicator in indicators:
            results.append(indicator.value().calculate(City(city, admin_level=4)))

    return results