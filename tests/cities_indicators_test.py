from cities_indicators.core import get_indicators, Indicator
from cities_indicators.city import SupportedCity


# def test_tree_cover_in_built_up_areas():
#     indicators = get_indicators(cities=[SupportedCity.IDN_Jakarta], indicators=[Indicator.BUILT_LAND_WITH_TREE_COVER])
#     print(indicators)

# def test_surface_reflectivity():
#     indicators = get_indicators(cities=[SupportedCity.IDN_Jakarta], indicators=[Indicator.SURFACE_REFLECTIVTY])
#     print(indicators)

# def test_land_surface_temperature():
#     indicators = get_indicators(cities=[SupportedCity.IDN_Jakarta], indicators=[Indicator.BUILT_LAND_WITH_HIGH_LST])
#     print(indicators)

def test_land_surface_temperature_gee():
    indicators = get_indicators(cities=[SupportedCity.IDN_Jakarta], indicators=[Indicator.BUILT_LAND_WITH_HIGH_LST_GEE])
    print(indicators)