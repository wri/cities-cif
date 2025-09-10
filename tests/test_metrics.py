import random
import math
import pytest

from city_metrix.metrics import *
from tests.conftest import EXECUTE_IGNORED_TESTS, IDN_JAKARTA_TILED_ZONES, IDN_JAKARTA_TILED_ZONES_SMALL, USA_OR_PORTLAND_ZONE, USA_OR_PORTLAND_TILED_LARGE_ZONE, ARG_BUENOS_AIRES_TILED_ZONES_TINY
PORTLAND_DST_seasonal_utc_offset = -8

# TODO Why do results all match for test_mean_pm2p5_exposure_popweighted


def test_area_fractional_vegetation_exceeds_threshold__percent():
    indicator = AreaFractionalVegetationExceedsThreshold__Percent().get_metric(ARG_BUENOS_AIRES_TILED_ZONES_TINY)
    expected_zone_size = len(ARG_BUENOS_AIRES_TILED_ZONES_TINY.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 82.37, 92.23, 3, 0)

def test_percent_built_area_without_tree_cover__percent():
    indicator = BuiltAreaWithoutTreeCover__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.00, 100.00, 28, 72)

def test_built_land_with_high_lst__percent():
    sample_zones = IDN_JAKARTA_TILED_ZONES
    indicator = BuiltLandWithHighLST__Percent().get_metric(sample_zones)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 1, 0.0, 10, 100, 0)

def test_built_land_with_low_surface_reflectivity__percent():
    indicator = BuiltLandWithLowSurfaceReflectivity__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 83, 99, 100, 0)

def test_built_land_with_vegetation__percent():
    indicator = BuiltLandWithVegetation__Percent().get_metric(ARG_BUENOS_AIRES_TILED_ZONES_TINY)
    expected_zone_size = len(ARG_BUENOS_AIRES_TILED_ZONES_TINY.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 1, 6.1, 17.2, 2, 1)

def test_canopy_area_per_resident_children__squaremeters():
    indicator = CanopyAreaPerResidentChildren__SquareMeters().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 5.24, 115.12, 100, 0)

def test_canopy_area_per_resident_elderly__squaremeters():
    indicator = CanopyAreaPerResidentElderly__SquareMeters().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 17.09, 375.27, 100, 0)

def test_canopy_area_per_resident_female__squaremeters():
    indicator = CanopyAreaPerResidentFemale__SquareMeters().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 2.33, 51.13, 100, 0)

def test_canopy_area_per_resident_informal__squaremeters():
    indicator = CanopyAreaPerResidentInformal__SquareMeters().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.00, 2.81, 18, 82)

def test_canopy_covered_population_children__percent():
    indicator = CanopyCoveredPopulationChildren__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size

def test_canopy_covered_population_elderly__percent():
    indicator = CanopyCoveredPopulationElderly__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size

def test_canopy_covered_population_female__percent():
    indicator = CanopyCoveredPopulationFemale__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size

def test_canopy_covered_population_informal__percent():
    indicator = CanopyCoveredPopulationInformal__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason="CDS API needs personal access token file to run")
def test_era_5_met_preprocess_umep():
    # Useful site: https://projects.oregonlive.com/weather/temps/
    indicator = (Era5MetPreprocessingUmep(start_date='2023-01-01', end_date='2023-12-31', seasonal_utc_offset=PORTLAND_DST_seasonal_utc_offset)
                 .get_metric(USA_OR_PORTLAND_ZONE))
    non_nullable_variables = ['temp', 'rh', 'global_rad', 'direct_rad', 'diffuse_rad', 'wind', 'vpd']
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
                              'GHI', 'Clearsky DHI', 'Clearsky DNI', 'Clearsky GHI',
                              'Wind Speed', 'Relative Humidity', 'Temperature', 'Pressure']
    has_empty_required_cells = indicator[non_nullable_variables].isnull().any().any()
    assert has_empty_required_cells == False
    assert len(indicator) == 24
    assert_metric_stats(indicator[['DHI']], 2, 0.00, 312.15, 24, 0)

def test_habitat_types_restored__covertypes():
    indicator = HabitatTypesRestored__CoverTypes().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0, 5, 100, 0)

def test_hospitals_per_ten_thousand_residents__hospitals():
    indicator = HospitalsPerTenThousandResidents__Hospitals().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.00, 8.87, 100, 0)

def test_impervious_area__percent():
    indicator = ImperviousArea__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 78.51, 100.00, 100, 0)

def test_impervious_surface_on_urbanized_land__percent():
    indicator = ImperviousSurfaceOnUrbanizedLand__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 78.512, 100, 100, 0)

def test_land_near_natural_drainage__percent():
    indicator = LandNearNaturalDrainage__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 1.753, 47.389, 98, 2)

def test_mean_pm2p5_exposure_popweighted_children__microgramspercubicmeter():
    indicator = MeanPM2P5ExposurePopWeightedChildren__MicrogramsPerCubicMeter().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 15.40, 62.79, 100, 0)

def test_mean_pm2p5_exposure_popweighted_elderly__microgramspercubicmeter():
    indicator = MeanPM2P5ExposurePopWeightedElderly__MicrogramsPerCubicMeter().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 15.40, 62.79, 100, 0)

def test_mean_pm2p5_exposure_popweighted_female__microgramspercubicmeter():
    indicator = MeanPM2P5ExposurePopWeightedFemale__MicrogramsPerCubicMeter().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 15.40, 62.79, 100, 0)

def test_mean_pm2p5_exposure_popweighted_informal__microgramspercubicmeter():
    indicator = MeanPM2P5ExposurePopWeightedInformal__MicrogramsPerCubicMeter().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, None, None, None, 0, 100)

def test_mean_tree_cover__percent():
    indicator = MeanTreeCover__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 1, 5.7, 32.6, 100, 0)

def test_natural_areas__percent():
    indicator = NaturalAreas__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.79, 56.29, 100, 0)

def test_number_species_bird_richness__species():
    random.seed(42)
    indicator = BirdRichness__Species().get_metric(IDN_JAKARTA_TILED_ZONES_SMALL)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES_SMALL.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 1, 7.0, 15.0, 2, 38)

def test_number_species_arthropod_richness__species():
    random.seed(42)
    indicator = ArthropodRichness__Species().get_metric(IDN_JAKARTA_TILED_ZONES_SMALL)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES_SMALL.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 1, 36.0, 36.0, 1, 39)

def test_number_species_vascular_plant_richness__species():
    random.seed(42)
    indicator = VascularPlantRichness__Species().get_metric(IDN_JAKARTA_TILED_ZONES_SMALL)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES_SMALL.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 1, 10.0, 10.0, 1, 39)

def test_number_species_bird_richness_in_builtup_area__species():
    random.seed(42)
    indicator = BirdRichnessInBuiltUpArea__Species().get_metric(IDN_JAKARTA_TILED_ZONES_SMALL)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES_SMALL.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 1, 7.0, 7.0, 1, 39)

def test_protected_area__percent():
    indicator = ProtectedArea__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.00, 0.00, 100, 0)

def test_recreational_space_per_thousand__hectaresperthousandpersons():
    spatial_resolution = 100
    indicator = (RecreationalSpacePerThousand__HectaresPerThousandPersons()
                 .get_metric(IDN_JAKARTA_TILED_ZONES, spatial_resolution=spatial_resolution))
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0, 0.455, 100, 0)

def test_riparian_land_with_vegetation_or_water__percent():
    indicator = RiparianLandWithVegetationOrWater__Percent().get_metric(ARG_BUENOS_AIRES_TILED_ZONES_TINY)
    expected_zone_size = len(ARG_BUENOS_AIRES_TILED_ZONES_TINY.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 77.75, 92.34, 3, 0)

def test_riverine_or_coastal_flood_risk_area__percent():
    indicator = RiverineOrCoastalFloodRiskArea__Percent().get_metric(USA_OR_PORTLAND_TILED_LARGE_ZONE)
    expected_zone_size = len(USA_OR_PORTLAND_TILED_LARGE_ZONE.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0, 100, 60, 219)

def test_steeply_sloped_land_with_vegetation__percent():
    indicator = SteeplySlopedLandWithVegetation__Percent().get_metric(ARG_BUENOS_AIRES_TILED_ZONES_TINY)
    expected_zone_size = len(ARG_BUENOS_AIRES_TILED_ZONES_TINY.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 79.41, 100, 2, 1)

def test_tree_carbon_flux__tonnes():
    indicator = TreeCarbonFlux__Tonnes().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, -39.046, 1.256, 100, 0)

def test_urban_open_space__percent():
    indicator = UrbanOpenSpace__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 3, 0, 2.083, 100, 0)

def test_vegetation_water_change_gain_area__squaremeters():
    indicator = VegetationWaterChangeGainArea__SquareMeters().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 0, 8300, 110300, 100, 0)

def test_vegetation_water_change_loss_area__squaremeters():
    indicator = VegetationWaterChangeLossArea__SquareMeters().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 0, 800, 41600, 100, 0)

def test_vegetation_water_change_gain_loss__ratio():
    indicator = VegetationWaterChangeGainLoss__Ratio().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, -0.0134, 0.2426, 100, 0)

def test_water_cover__percent():
    indicator = WaterCover__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0, 0.081, 100, 0)


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

def assert_metric_stats(data, sig_digits: int, min_notnull_val, max_notnull_val, notnull_count: int, null_count: int):
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
