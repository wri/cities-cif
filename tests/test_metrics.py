from city_metrix import *
from .conftest import ZONES, EXECUTE_IGNORED_TESTS
import pytest



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


def test_built_land_without_tree_cover():
    indicator = built_land_without_tree_cover(ZONES)
    expected_zone_size = ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size

def test_count_accessible_amenities():
    from .conftest import create_fishnet_grid
    NAIROBI_BBOX = create_fishnet_grid(36.66446402, -1.44560888, 37.10497899, -1.16058296, 0.01).reset_index()
    indicator = count_accessible_amenities(NAIROBI_BBOX, 'KEN-Nairobi', 'schools', 'walk', 'time', '15', 2024, aws_profilename=None)
    expected_zone_size = NAIROBI_BBOX.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason="CDS API needs personal access token file to run")
def test_era_5_met_preprocess():
    indicator = era_5_met_preprocessing(ZONES)
    assert len(indicator) == 24


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

def test_percent_population_access():
    from .conftest import create_fishnet_grid
    NAIROBI_BBOX = create_fishnet_grid(36.66446402, -1.44560888, 37.10497899, -1.16058296, 0.01).reset_index()
    indicator = percent_population_access(NAIROBI_BBOX, 'KEN-Nairobi', 'schools', 'walk', 'time', '15', 2024, aws_profilename=None)
    expected_zone_size = NAIROBI_BBOX.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size

def test_recreational_space_per_capita():
    indicator = recreational_space_per_capita(ZONES)
    expected_zone_size = ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size


def test_urban_open_space():
    indicator = urban_open_space(ZONES)
    expected_zone_size = ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size
