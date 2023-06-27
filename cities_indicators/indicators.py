from typing import List
from enum import Enum

class Indicator(Enum):
    ACC2 = "Tropical tree cover in built up areas"


class City(Enum):
    # TODO how can we programmatically figure out what admin boundaries to use?
    ARG_3_1 = "Buenos Aires"


def get_indicators(cities: List[City], indicators: List[Indicator]):
    results = []
    for city in cities:
        for indicator in indicators:
            results.append(Indicator.calculate(indicator, city))

    return results