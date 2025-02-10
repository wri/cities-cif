from city_metrix import *
from .conftest import IDN_JAKARTA_TILED_ZONES, EXECUTE_IGNORED_TESTS, USA_OR_PORTLAND_TILE_GDF, NLD_AMSTERDAM_TILE_GDF
import pytest


def test_built_land_with_high_lst():
    sample_zones = IDN_JAKARTA_TILED_ZONES
    indicator = built_land_with_high_land_surface_temperature(sample_zones)
    expected_zone_size = IDN_JAKARTA_TILED_ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size


def test_built_land_with_low_surface_reflectivity():
    indicator = built_land_with_low_surface_reflectivity(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = IDN_JAKARTA_TILED_ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size


def test_built_land_without_tree_cover():
    indicator = built_land_without_tree_cover(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = IDN_JAKARTA_TILED_ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size


@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason="CDS API needs personal access token file to run")
def test_era_5_met_preprocess():
    # Useful site: https://projects.oregonlive.com/weather/temps/
    indicator = era_5_met_preprocessing(USA_OR_PORTLAND_TILE_GDF)
    non_nullable_variables = ['temp','rh','global_rad','direct_rad','diffuse_rad','wind','vpd']
    has_empty_required_cells = indicator[non_nullable_variables].isnull().any().any()
    # p1= indicator[non_nullable_variables].isnull().any()
    # p2 = indicator['global_rad'].values
    # p3 = indicator['temp'].values
    assert has_empty_required_cells == False
    assert len(indicator) == 24


def test_mean_tree_cover():
    indicator = mean_tree_cover(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = IDN_JAKARTA_TILED_ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size


def test_natural_areas():
    indicator = natural_areas(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = IDN_JAKARTA_TILED_ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size


def test_recreational_space_per_capita():
    spatial_resolution=100
    indicator = recreational_space_per_capita(IDN_JAKARTA_TILED_ZONES, spatial_resolution=spatial_resolution)
    expected_zone_size = IDN_JAKARTA_TILED_ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size


def test_pop_open_space():
    indicator = pop_open_space(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = IDN_JAKARTA_TILED_ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size


def test_urban_open_space():
    indicator = urban_open_space(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = IDN_JAKARTA_TILED_ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size


def test_vegetation_water_change_gain_area():
    indicator = vegetation_water_change_gain_area(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = IDN_JAKARTA_TILED_ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size


def test_vegetation_water_change_loss_area():
    indicator = vegetation_water_change_loss_area(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = IDN_JAKARTA_TILED_ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size


def test_vegetation_water_change_gain_loss_ratio():
    indicator = vegetation_water_change_gain_loss_ratio(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = IDN_JAKARTA_TILED_ZONES.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size
