from cities_indicators.core import get_indicators, Indicator
from cities_indicators.io import export_results
from cities_indicators.city import get_city


def test_tree_cover_in_built_up_areas():
    jakarta = get_city("IDN-Jakarta")
    indicators = get_indicators(cities=[jakarta], indicators=[Indicator.BUILT_LAND_WITH_TREE_COVER])
    print(indicators)


def test_surface_reflectivity():
    jakarta = get_city("IDN-Jakarta")
    indicators = get_indicators(cities=[jakarta], indicators=[Indicator.SURFACE_REFLECTIVTY])
    print(indicators)

def test_tree_cover():
    jakarta = get_city("IDN-Jakarta")
    indicators = get_indicators(cities=[jakarta], indicators=[Indicator.TREE_COVER])
    print(indicators)
