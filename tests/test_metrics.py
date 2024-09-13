from city_metrix import *
from city_metrix.metrics.built_land_with_vegetation import built_land_with_vegetation
from .conftest import ZONES


def test_built_land_with_high_lst():
    indicator = built_land_with_high_land_surface_temperature(ZONES)
    expected_zone_size = ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size


def test_built_land_with_low_surface_reflectivity():
    indicator = built_land_with_low_surface_reflectivity(ZONES)
    expected_zone_size = ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size

def test_built_land_with_vegetation():
    indicator = built_land_with_vegetation(ZONES)
    expected_zone_size = ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size

def test_built_land_without_tree_cover():
    indicator = built_land_without_tree_cover(ZONES)
    expected_zone_size = ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size


def test_mean_tree_cover():
    indicator = mean_tree_cover(ZONES)
    expected_zone_size = ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size


def test_natural_areas():
    indicator = natural_areas(ZONES)
    expected_zone_size = ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size


def test_urban_open_space():
    indicator = urban_open_space(ZONES)
    expected_zone_size = ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size