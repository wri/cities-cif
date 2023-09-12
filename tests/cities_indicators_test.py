from cities_indicators.core import get_indicators, Indicator
from cities_indicators.io import export_results
from cities_indicators.city import get_city
import ee


def test_tree_cover_in_built_up_areas():
    jakarta = get_city("IDN-Jakarta")
    indicators = get_indicators(cities=[jakarta], indicators=[Indicator.BUILT_LAND_WITH_TREE_COVER])
    indicators[0].to_csv("jakarta-tc-built-s3.csv")


def test_surface_reflectivity():
    jakarta = get_city("IDN-Jakarta")
    indicators = get_indicators(cities=[jakarta], indicators=[Indicator.SURFACE_REFLECTIVTY])
    indicators[0].to_csv("albedo.csv")
    print(indicators)

def test_tree_cover():
    jakarta = get_city("IDN-Jakarta")
    indicators = get_indicators(cities=[jakarta], indicators=[Indicator.TREE_COVER])
    print(indicators)
