from cities_indicators.core import get_indicators, Indicator
from cities_indicators.city import SupportedCity


def _test_tree_cover_in_built_up_areas():
    indicators = get_indicators(cities=[SupportedCity.IDN_Jakarta], indicators=[Indicator.BUILT_LAND_WITH_TREE_COVER])
    print(indicators)
    assert False

def test_surface_reflectivity():
    indicators = get_indicators(cities=[SupportedCity.IDN_Jakarta], indicators=[Indicator.SURFACE_REFLECTIVTY])
    print(indicators)