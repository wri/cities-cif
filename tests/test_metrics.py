import math
import pytest

from city_metrix.metrics import *
from .conftest import IDN_JAKARTA_TILED_ZONES, EXECUTE_IGNORED_TESTS, USA_OR_PORTLAND_ZONE, BUENOS_AIRES_ZONES
PORTLAND_DST_seasonal_utc_offset = -8


# TODO Why do results all match for test_mean_pm2p5_exposure_popweighted

def test_built_land_with_high_lst():
    sample_zones = IDN_JAKARTA_TILED_ZONES
    indicator = BuiltLandWithHighLST().get_metric(sample_zones)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 1, 0.0, 0.1, 100, 0)

def test_built_land_with_low_surface_reflectivity():
    indicator = BuiltLandWithLowSurfaceReflectivity().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.83, 0.99, 100, 0)

def test_canopy_area_per_resident_children():
    indicator = CanopyAreaPerResidentChildren().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 5.24, 115.12, 100, 0)

def test_canopy_area_per_resident_elderly():
    indicator = CanopyAreaPerResidentElderly().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 17.09, 375.27, 100, 0)

def test_canopy_area_per_resident_female():
    indicator = CanopyAreaPerResidentFemale().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 2.33, 51.13, 100, 0)

def test_canopy_area_per_resident_informal():
    indicator = CanopyAreaPerResidentInformal().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.00, 2.81, 18, 82)

def test_hospitals_per_ten_thousand_residents():
    indicator = HospitalsPerTenThousandResidents().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.00, 8.87, 100, 0)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason="CDS API needs personal access token file to run")
def test_era_5_met_preprocess_umep():
    # Useful site: https://projects.oregonlive.com/weather/temps/
    indicator = (Era5MetPreprocessingUmep(start_date='2023-01-01', end_date='2023-12-31', seasonal_utc_offset=PORTLAND_DST_seasonal_utc_offset)
                 .get_metric(USA_OR_PORTLAND_ZONE))
    non_nullable_variables = ['temp','rh','global_rad','direct_rad','diffuse_rad','wind','vpd']
    has_empty_required_cells = indicator[non_nullable_variables].isnull().any().any()
    # p1= indicator[non_nullable_variables].isnull().any()
    # p2 = indicator['global_rad'].values
    # p3 = indicator['temp'].values
    assert has_empty_required_cells == False
    assert len(indicator) == 24
    assert_metric_stats(indicator[['temp']], 2, 19.19, 41.36, 24, 0)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason="CDS API needs personal access token file to run")
def test_era_5_met_preprocess_upenn():
    # Useful site: https://projects.oregonlive.com/weather/temps/
    indicator = (Era5MetPreprocessingUPenn(start_date='2023-01-01', end_date='2023-12-31', seasonal_utc_offset=PORTLAND_DST_seasonal_utc_offset)
                 .get_metric(USA_OR_PORTLAND_ZONE))

    non_nullable_variables = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'DHI', 'DNI', 
                              'GHI', 'Clearsky DHI', 'Clearsky DNI','Clearsky GHI', 
                              'Wind Speed', 'Relative Humidity', 'Temperature', 'Pressure']
    has_empty_required_cells = indicator[non_nullable_variables].isnull().any().any()
    assert has_empty_required_cells == False
    assert len(indicator) == 24
    assert_metric_stats(indicator[['DHI']], 2, 0.00, 312.15, 24, 0)

def test_kba_protected():
    indicator = KeyBiodiversityAreaProtected__Percent().get_metric(BUENOS_AIRES_ZONES)
    expected_zone_size = len(BUENOS_AIRES_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 1.19, 100, 15, 84)

def test_kba_undeveloped():
    indicator = KeyBiodiversityAreaUndeveloped__Percent().get_metric(BUENOS_AIRES_ZONES)
    expected_zone_size = len(BUENOS_AIRES_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 40.22, 99.99, 12, 87)

def test_impervious_surface_on_urbanized_land__percent():
    indicator = ImperviousSurfaceOnUrbanizedLand__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 78.512, 100, 100, 0)

def test_mean_pm2p5_exposure_popweighted_children():
    indicator = MeanPM2P5ExposurePopWeightedChildren().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 15.40, 62.79, 100, 0)

def test_mean_pm2p5_exposure_popweighted_elderly():
    indicator = MeanPM2P5ExposurePopWeightedElderly().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 15.40, 62.79, 100, 0)

def test_mean_pm2p5_exposure_popweighted_female():
    indicator = MeanPM2P5ExposurePopWeightedFemale().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 15.40, 62.79, 100, 0)

def test_mean_pm2p5_exposure_popweighted_informal():
    indicator = MeanPM2P5ExposurePopWeightedInformal().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, None, None, None, 0, 100)

def test_mean_tree_cover():
    indicator = MeanTreeCover().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.057, 0.326, 100, 0)

def test_natural_areas__percent():
    indicator = NaturalAreas__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.79, 56.29, 100, 0)

def test_percent_area_fracveg_exceeds_threshold():
    indicator = PercentAreaFracvegExceedsThreshold().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.0101, 0.334, 100, 0)

def test_percent_area_impervious():
    indicator = PercentAreaImpervious().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 78.51, 100.00, 100, 0)

def test_percent_built_area_without_tree_cover():
    indicator = PercentBuiltAreaWithoutTreeCover().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 36.36, 100, 54, 46)

def test_percent_canopy_covered_population_children():
    indicator = PercentCanopyCoveredPopulationChildren().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size

def test_percent_canopy_covered_population_elderly():
    indicator = PercentCanopyCoveredPopulationElderly().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size

def test_percent_canopy_covered_population_female():
    indicator = PercentCanopyCoveredPopulationFemale().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size

def test_percent_canopy_covered_population_informal():
    indicator = PercentCanopyCoveredPopulationInformal().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size

def test_percent_protected_area():
    indicator = PercentProtectedArea().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.00, 0.00, 100, 0)

def test_recreational_space_per_capita():
    spatial_resolution=100
    indicator = (RecreationalSpacePerCapita()
                 .get_metric(IDN_JAKARTA_TILED_ZONES, spatial_resolution=spatial_resolution))
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0, 0.455, 100, 0)

def test_urban_open_space():
    indicator = UrbanOpenSpace().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 3, 0, 0.02083, 100, 0)

def test_vegetation_water_change_gain_area():
    indicator = VegetationWaterChangeGainArea().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 0, 8300, 110300, 100, 0)

def test_vegetation_water_change_loss_area():
    indicator = VegetationWaterChangeLossArea().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 0, 800, 41600, 100, 0)

def test_vegetation_water_change_gain_loss_ratio():
    indicator = VegetationWaterChangeGainLossRatio().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, -0.0134, 0.2426, 100, 0)


def _eval_numeric(sig_digits, data_min_notnull_val, data_max_notnull_val, data_notnull_count, data_null_count,
                  min_notnull_val, max_notnull_val, notnull_count, null_count):
    if sig_digits is not None:
        float_tol = (10 ** -sig_digits)
        is_matched = (math.isclose(round(data_min_notnull_val, sig_digits), round(min_notnull_val, sig_digits), rel_tol=float_tol)
                      and math.isclose(round(data_max_notnull_val, sig_digits), round(max_notnull_val, sig_digits), rel_tol=float_tol)
                      and data_notnull_count == notnull_count
                      and data_null_count == null_count
                      )

        expected = f"{min_notnull_val:.{sig_digits}f}, {max_notnull_val:.{sig_digits}f}, {notnull_count}, {null_count}"
        actual = f"{data_min_notnull_val:.{sig_digits}f}, {data_max_notnull_val:.{sig_digits}f}, {data_notnull_count}, {data_null_count}"
    else:
        is_matched = (compare_nullable_numbers(data_min_notnull_val, min_notnull_val)
                      and compare_nullable_numbers(data_max_notnull_val, max_notnull_val)
                      and data_notnull_count == notnull_count
                      and data_null_count == null_count
                      )

        expected = f"{min_notnull_val}, {max_notnull_val}, {notnull_count}, {null_count}"
        actual = f"{data_min_notnull_val}, {data_max_notnull_val}, {data_notnull_count}, {data_null_count}"

    return is_matched, expected, actual

def compare_nullable_numbers(a, b):
    if a is None and b is None:
        return True
    return a == b

def assert_metric_stats(data, sig_digits:int, min_notnull_val, max_notnull_val, notnull_count:int, null_count:int):
    if 'zone' in data.columns:
        data = data.drop(columns=['zone'])

    data = data.squeeze()

    min_val = data.dropna().min()
    data_min_notnull_val = None if pd.isna(min_val) else min_val
    max_val = data.dropna().max()
    data_max_notnull_val = None if pd.isna(max_val) else max_val
    data_notnull_count = data.count()
    data_null_count = data.isnull().sum()

    is_matched, expected, actual = _eval_numeric(sig_digits, data_min_notnull_val, data_max_notnull_val,
                  data_notnull_count, data_null_count, min_notnull_val, max_notnull_val, notnull_count, null_count)
    assert is_matched, f"expected ({expected}), but got ({actual})"

    # template
    # assert_metric_stats(indicator, 2, 0, 0, 1, 0)
