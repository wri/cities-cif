import pytest

from city_metrix.metrics import *
from .conftest import IDN_JAKARTA_TILED_ZONES, USA_OR_PORTLAND_ZONE, EXECUTE_IGNORED_TESTS
from .tools.general_tools import assert_metric_stats


# TODO Why do results all match for test_mean_pm2p5_exposure_popweighted

def test_built_land_with_high_lst():
    sample_zones = IDN_JAKARTA_TILED_ZONES
    indicator = BuiltLandWithHighLST().get_data(sample_zones)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 1, 0.0, 0.1, 100, 0)

def test_built_land_with_low_surface_reflectivity():
    indicator = BuiltLandWithLowSurfaceReflectivity().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.83, 0.99, 100, 0)

def test_built_land_without_tree_cover():
    indicator = BuiltLandWithoutTreeCover().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.65, 0.93, 100, 0)

def test_canopy_area_per_resident_children():
    indicator = CanopyAreaPerResidentChildren().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 5.24, 115.12, 100, 0)

def test_canopy_area_per_resident_elderly():
    indicator = CanopyAreaPerResidentElderly().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 17.09, 375.27, 100, 0)

def test_canopy_area_per_resident_female():
    indicator = CanopyAreaPerResidentFemale().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 2.33, 51.13, 100, 0)

def test_canopy_area_per_resident_informal():
    indicator = CanopyAreaPerResidentInformal().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.00, 2.81, 18, 82)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason="CDS API needs personal access token file to run")
def test_era_5_met_preprocess():
    # Useful site: https://projects.oregonlive.com/weather/temps/
    indicator = Era5MetPreprocessing().get_data(USA_OR_PORTLAND_ZONE)
    non_nullable_variables = ['temp','rh','global_rad','direct_rad','diffuse_rad','wind','vpd']
    has_empty_required_cells = indicator[non_nullable_variables].isnull().any().any()
    # p1= indicator[non_nullable_variables].isnull().any()
    # p2 = indicator['global_rad'].values
    # p3 = indicator['temp'].values
    assert has_empty_required_cells == False
    assert len(indicator) == 24
    # TODO Add value testing

def test_mean_pm2p5_exposure_popweighted_children():
    indicator = MeanPM2P5ExposurePopWeightedChildren().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 20.64, 51.63, 100, 0)

def test_mean_pm2p5_exposure_popweighted_elderly():
    indicator = MeanPM2P5ExposurePopWeightedElderly().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 20.64, 51.63, 100, 0)

def test_mean_pm2p5_exposure_popweighted_female():
    indicator = MeanPM2P5ExposurePopWeightedFemale().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 20.64, 51.63, 100, 0)

def test_mean_pm2p5_exposure_popweighted_informal():
    indicator = MeanPM2P5ExposurePopWeightedInformal().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, None, None, None, 0, 100)

def test_mean_tree_cover():
    indicator = MeanTreeCover().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.057, 0.326, 100, 0)

def test_natural_areas():
    indicator = NaturalAreasPercent().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.79, 56.29, 100, 0)

def test_percent_area_impervious():
    indicator = PercentAreaImpervious().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 78.51, 100.00, 100, 0)

def test_percent_protected_area():
    indicator = PercentProtectedArea().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.00, 0.00, 100, 0)

def test_recreational_space_per_capita():
    spatial_resolution=100
    indicator = (RecreationalSpacePerCapita()
                 .get_data(IDN_JAKARTA_TILED_ZONES, spatial_resolution=spatial_resolution))
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0, 0.455, 100, 0)

def test_urban_open_space():
    indicator = UrbanOpenSpace().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 3, 0, 0.02036, 100, 0)

def test_vegetation_water_change_gain_area():
    indicator = VegetationWaterChangeGainArea().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 0, 8300, 110300, 100, 0)

def test_vegetation_water_change_loss_area():
    indicator = VegetationWaterChangeLossArea().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 0, 800, 41600, 100, 0)

def test_vegetation_water_change_gain_loss_ratio():
    indicator = VegetationWaterChangeGainLossRatio().get_data(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, -0.0134, 0.2426, 100, 0)
