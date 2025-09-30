import random
import math
import pytest

from city_metrix.metrics import *
from tests.conftest import EXECUTE_IGNORED_TESTS, IDN_JAKARTA_TILED_ZONES, IDN_JAKARTA_TILED_ZONES_SMALL, USA_OR_PORTLAND_ZONE, USA_OR_PORTLAND_TILED_LARGE_ZONE, ARG_BUENOS_AIRES_TILED_ZONES, ARG_BUENOS_AIRES_TILED_ZONES_TINY
from tests.resources.bbox_constants import GEOZONE_TERESINA
PORTLAND_DST_seasonal_utc_offset = -8


def test_access_to_openspace_female__percent():
    indicator = AccessToOpenSpaceFemale__Percent(travel_mode='walk', threshold=15, unit='minutes').get_metric(GEOZONE_TERESINA)
    expected_zone_size = len(GEOZONE_TERESINA.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.0, 28.537361096287057, 67, 72)

def test_access_to_openspace_informal__percent():
    indicator = AccessToOpenSpaceInformal__Percent(travel_mode='walk', threshold=15, unit='minutes').get_metric(GEOZONE_TERESINA)
    expected_zone_size = len(GEOZONE_TERESINA.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.0, 28.537360907512625, 67, 72)

def test_access_to_schools_children__percent():
    indicator = AccessToSchoolsChildren__Percent(travel_mode='walk', threshold=15, unit='minutes').get_metric(GEOZONE_TERESINA)
    expected_zone_size = len(GEOZONE_TERESINA.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.0, 71.97229979366347, 67, 72)

def test_access_to_goodsandservices_female__percent():
    indicator = AccessToGoodsAndServicesFemale__Percent(travel_mode='walk', threshold=15, unit='minutes').get_metric(GEOZONE_TERESINA)
    expected_zone_size = len(GEOZONE_TERESINA.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.0, 25.326068167411968, 67, 72)

def test_access_to_goodsandservices_informal__percent():
    indicator = AccessToGoodsAndServicesInformal__Percent(travel_mode='walk', threshold=15, unit='minutes').get_metric(GEOZONE_TERESINA)
    expected_zone_size = len(GEOZONE_TERESINA.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.0, 25.326064146273673, 67, 72)

def test_access_to_potentialemployment_female__percent():
    indicator = AccessToPotentialEmploymentFemale__Percent(travel_mode='walk', threshold=15, unit='minutes').get_metric(GEOZONE_TERESINA)
    expected_zone_size = len(GEOZONE_TERESINA.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.0, 25.326068167411968, 67, 72)

def test_access_to_publictransportation_children__percent():
    indicator = AccessToPublicTransportationChildren__Percent(travel_mode='walk', threshold=15, unit='minutes').get_metric(GEOZONE_TERESINA)
    expected_zone_size = len(GEOZONE_TERESINA.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.0, 29.363878163274165, 67, 72)

def test_access_to_healthcare_elderly__percent():
    indicator = AccessToHealthcareElderly__Percent(travel_mode='walk', threshold=15, unit='minutes').get_metric(GEOZONE_TERESINA)
    expected_zone_size = len(GEOZONE_TERESINA.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.0, 2.9866815956816017, 67, 72)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason="CDS API needs personal access token file to run")
def test_air_pollutant_annual_daily_max__tonnes():
    indicator = AirPollutantAnnualDailyMax__Tonnes().get_metric(IDN_JAKARTA_TILED_ZONES)
    assert indicator.size > 0 # Note that this metric returns same size result regardless of geometry size

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason="CDS API needs personal access token file to run")
def test_air_pollutant_annual_daily_mean__tonnes():
    indicator = AirPollutantAnnualDailyMean__Tonnes().get_metric(IDN_JAKARTA_TILED_ZONES)
    assert indicator.size > 0 # Note that this metric returns same size result regardless of geometry size

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason="CDS API needs personal access token file to run")
def test_air_pollutant_annual_total_social_cost__usd():
    indicator = AirPollutantAnnualTotalSocialCost__USD().get_metric(IDN_JAKARTA_TILED_ZONES)
    assert indicator.size > 0 # Note that this metric returns same size result regardless of geometry size

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason="CDS API needs personal access token file to run")
def test_air_pollutant_who_exceedance__days():
    indicator = AirPollutantWhoExceedance__Days().get_metric(IDN_JAKARTA_TILED_ZONES)
    assert indicator.size > 0 # Note that this metric returns same size result regardless of geometry size

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
    assert_metric_stats(indicator, 2, 89.00, 97.94, 100, 0)

def test_built_land_with_high_lst__percent():
    indicator = BuiltLandWithHighLST__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
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
    assert_metric_stats(indicator, 2, 5.32, 115.07, 100, 0)

def test_canopy_area_per_resident_elderly__squaremeters():
    indicator = CanopyAreaPerResidentElderly__SquareMeters().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 17.34, 375.10, 100, 0)

def test_canopy_area_per_resident_female__squaremeters():
    indicator = CanopyAreaPerResidentFemale__SquareMeters().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 2.36, 51.11, 100, 0)

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

def test_count_potential_employers_elderly_popweighted__count():
    indicator = CountPotentialEmployersElderlyPopWeighted__Count(travel_mode='walk', threshold=15, unit='minutes').get_metric(GEOZONE_TERESINA)
    expected_zone_size = len(GEOZONE_TERESINA.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.0, 50308.607206042594, 139, 0)

def test_count_potential_employers_informal_popweighted__count():
    indicator = CountPotentialEmployersInformalPopWeighted__Count(travel_mode='walk', threshold=15, unit='minutes').get_metric(GEOZONE_TERESINA)
    expected_zone_size = len(GEOZONE_TERESINA.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.0, 91.58, 139, 0)

# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason="CDS API needs personal access token file to run")
def test_era5_met_preprocess_umep():
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
    assert_metric_stats(indicator[['temp']], 2, 18.90, 41.37, 24, 0)

# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason="CDS API needs personal access token file to run")
def test_era5_met_preprocess_upenn():
    # Useful site: https://projects.oregonlive.com/weather/temps/
    indicator = (Era5MetPreprocessingUPenn(start_date='2023-01-01', end_date='2023-12-31', seasonal_utc_offset=PORTLAND_DST_seasonal_utc_offset)
                 .get_metric(USA_OR_PORTLAND_ZONE))
    non_nullable_variables = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'DHI', 'DNI',
                              'GHI', 'Clearsky DHI', 'Clearsky DNI', 'Clearsky GHI',
                              'Wind Speed', 'Relative Humidity', 'Temperature', 'Pressure']
    has_empty_required_cells = indicator[non_nullable_variables].isnull().any().any()
    assert has_empty_required_cells == False
    assert len(indicator) == 24
    assert_metric_stats(indicator[['DHI']], 2, 0.00, 312.33, 24, 0)

def test_future_annual_max_temp__degreescelsius():
    indicator = FutureAnnualMaxTemp__DegreesCelsius(model_rank=1).get_metric(IDN_JAKARTA_TILED_ZONES)
    assert len(indicator) == 1
    assert_metric_stats(indicator, 2, 34.9, 34.9, 1, 0)

def test_future_days_above_35__days():
    indicator = FutureDaysAbove35__Days(model_rank=1).get_metric(IDN_JAKARTA_TILED_ZONES)
    assert len(indicator) == 1
    assert_metric_stats(indicator, 2, 1.7, 1.7, 1, 0)

def test_future_extreme_precipitation__days():
    indicator = FutureExtremePrecipitationDays__Days(model_rank=1).get_metric(IDN_JAKARTA_TILED_ZONES)
    assert len(indicator) == 1
    assert_metric_stats(indicator, 1, 1, 1, 1, 0)

def test_future_heatwave_frequency__heatwaves():
    indicator = FutureHeatwaveFrequency__Heatwaves(model_rank=1).get_metric(IDN_JAKARTA_TILED_ZONES)
    assert len(indicator) == 1
    assert_metric_stats(indicator, 2, 22.1, 22.1, 1, 0)

def test_future_heatwave_max_duration__days():
    indicator = FutureHeatwaveMaxDuration__Days(model_rank=1).get_metric(IDN_JAKARTA_TILED_ZONES)
    assert len(indicator) == 1
    assert_metric_stats(indicator, 2, 81.6, 81.6, 1, 0)

def test_ghg_emissions__tonnes():
    indicator = GhgEmissions__Tonnes().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 3173212.00, 3173212.00, 100, 0)

def test_habitat_connectivity_coherence__percent():
    indicator = HabitatConnectivityCoherence__Percent().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 14.69, 100, 100, 0)

def test_habitat_connectivity_effective_mesh_size__hectares():
    indicator = HabitatConnectivityEffectiveMeshSize__Hectares().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.35, 74.81, 100, 0)

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
    assert_metric_stats(indicator, 2, 0.00, 0.00, 100, 0)

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

def test_key_biodiversity_area_protected__percent():
    indicator = KeyBiodiversityAreaProtected__Percent(country_code_iso3='ARG').get_metric(ARG_BUENOS_AIRES_TILED_ZONES)
    expected_zone_size = len(ARG_BUENOS_AIRES_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.00, 6.55, 7, 92)

def test_key_biodiversity_area_undeveloped__percent():
    indicator = KeyBiodiversityAreaUndeveloped__Percent(country_code_iso3='ARG').get_metric(ARG_BUENOS_AIRES_TILED_ZONES)
    expected_zone_size = len(ARG_BUENOS_AIRES_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 0.00, 76.27, 7, 92)

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
    assert_metric_stats(indicator, 2, 20.21, 67.67, 100, 0)

def test_mean_pm2p5_exposure_popweighted_elderly__microgramspercubicmeter():
    indicator = MeanPM2P5ExposurePopWeightedElderly__MicrogramsPerCubicMeter().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 20.21, 67.67, 100, 0)

def test_mean_pm2p5_exposure_popweighted_female__microgramspercubicmeter():
    indicator = MeanPM2P5ExposurePopWeightedFemale__MicrogramsPerCubicMeter().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 20.21, 67.67, 100, 0)

def test_mean_pm2p5_exposure_popweighted_informal__microgramspercubicmeter():
    indicator = MeanPM2P5ExposurePopWeightedInformal__MicrogramsPerCubicMeter().get_metric(IDN_JAKARTA_TILED_ZONES)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 2, 18.91, 62.39, 18, 82)

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
    assert_metric_stats(indicator, 1, 11.0, 11.0, 1, 39)

def test_number_species_arthropod_richness__species():
    random.seed(42)
    indicator = ArthropodRichness__Species().get_metric(IDN_JAKARTA_TILED_ZONES_SMALL)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES_SMALL.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, 1, 33.0, 33.0, 1, 39)

def test_number_species_vascular_plant_richness__species():
    random.seed(42)
    indicator = VascularPlantRichness__Species().get_metric(IDN_JAKARTA_TILED_ZONES_SMALL)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES_SMALL.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, None, None, None, 0, 40)

def test_number_species_bird_richness_in_builtup_area__species():
    random.seed(42)
    indicator = BirdRichnessInBuiltUpArea__Species().get_metric(IDN_JAKARTA_TILED_ZONES_SMALL)
    expected_zone_size = len(IDN_JAKARTA_TILED_ZONES_SMALL.zones)
    actual_indicator_size = len(indicator)
    assert expected_zone_size == actual_indicator_size
    assert_metric_stats(indicator, None, None, None, 0, 40)

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
