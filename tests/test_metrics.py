from city_metrix import *
from city_metrix.metrics.built_land_with_tree_cover import built_land_with_tree_cover
from .conftest import ZONES


def test_urban_open_space():
    indicator = urban_open_space(ZONES)
    assert indicator.size == 100


def test_built_land_with_low_surface_reflectivity():
    indicator = built_land_with_low_surface_reflectivity(ZONES)
    assert indicator.size == 100


def test_high_lst():
    indicator = built_land_with_high_land_surface_temperature(ZONES)
    assert indicator.size == 100

def test_built_land_with_tree_cover():
    indicator = built_land_with_tree_cover(ZONES)
    expected_zone_size = ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size