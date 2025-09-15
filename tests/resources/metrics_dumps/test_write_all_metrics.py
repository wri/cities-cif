# This code is mostly intended for manual execution
# Execution configuration is specified in the conftest file
import pytest

from city_metrix.constants import DEFAULT_DEVELOPMENT_ENV, CIF_TESTING_S3_BUCKET_URI
from city_metrix.metrics import *
from tests.conftest import create_fishnet_gdf_for_testing
from tests.resources.bbox_constants import BBOX_IDN_JAKARTA, BBOX_IDN_JAKARTA_LARGE
from tests.resources.conftest import DUMP_RUN_LEVEL, DumpRunLevel
from tests.resources.tools import prep_output_path, verify_file_is_populated, cleanup_cache_files

SAMPLE_TILED_SINGLE_ZONE = (
    GeoZone(create_fishnet_gdf_for_testing(BBOX_IDN_JAKARTA.coords, 0.1).reset_index()))

SAMPLE_TILED_ZONES = (
    GeoZone(create_fishnet_gdf_for_testing(BBOX_IDN_JAKARTA.coords, 0.05).reset_index()))

SAMPLE_TILED_LARGE_ZONES = (
    GeoZone(create_fishnet_gdf_for_testing(BBOX_IDN_JAKARTA_LARGE.coords, 0.5).reset_index()))

# TODO - groupby fails for small zones that return null values from AcagPM2p5 layer. How should system handle such nulls

PRESERVE_RESULTS_ON_OS = False  # False - Default for check-in


@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_area_fractional_vegetation_exceeds_threshold__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'area_fractional_vegetation_exceeds_threshold__percent.csv')

    metric_obj = AreaFractionalVegetationExceedsThreshold__Percent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_built_area_without_tree_cover__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'built_area_without_tree_cover__percent.csv')

    metric_obj = BuiltAreaWithoutTreeCover__Percent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_built_land_with_high_land_surface_temperature__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'built_land_with_high_land_surface_temperature__percent.csv')

    metric_obj = BuiltLandWithHighLST__Percent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_built_land_with_low_surface_reflectivity__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'built_land_with_low_surface_reflectivity__percent.csv')

    metric_obj = BuiltLandWithLowSurfaceReflectivity__Percent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_built_land_with_vegetation__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'built_land_with_vegetation__percent.csv')

    metric_obj = BuiltLandWithVegetation__Percent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_canopy_area_per_resident_children__squaremeters(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'canopy_area_per_resident_children__squaremeters.csv')

    metric_obj = CanopyAreaPerResidentChildren__SquareMeters()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_canopy_area_per_resident_elderly__squaremeters(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'canopy_area_per_resident_elderly__squaremeters.csv')

    metric_obj = CanopyAreaPerResidentElderly__SquareMeters()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_canopy_area_per_resident_female__squaremeters(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'canopy_area_per_resident_female__squaremeters.csv')

    metric_obj = CanopyAreaPerResidentFemale__SquareMeters()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_canopy_area_per_resident_informal__squaremeters(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'canopy_area_per_resident_informal__squaremeters.csv')

    metric_obj = CanopyAreaPerResidentInformal__SquareMeters()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_canopy_covered_population__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'canopy_covered_population__percent.csv')

    metric_obj = CanopyCoveredPopulation__Percent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_era_5_met_preprocessingUmep(target_folder):
    zones = SAMPLE_TILED_SINGLE_ZONE
    file_path = prep_output_path(
        target_folder, 'metric', 'era_5_met_preprocessing.csv')

    metric_obj = Era5MetPreprocessingUmep(
        start_date='2023-01-01', end_date='2023-12-31', seasonal_utc_offset=-8)
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_habitat_connectivity_coherence__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'habitat_connectivity_coherence__percent.csv')

    metric_obj = HabitatConnectivityCoherence__Percent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_habitat_connectivity_effective_mesh_size__hectares(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'habitat_connectivity_effective_mesh_size__hectares.csv')

    metric_obj = HabitatConnectivityEffectiveMeshSize__Hectares()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_habitat_types_restored__covertypes(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'habitat_types_restored__covertypes.csv')

    metric_obj = HabitatTypesRestored__CoverTypes()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_hospitals_per_ten_thousand_residents__hospitals(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'hospitals_per_ten_thousand_residents__hospitals.csv')

    metric_obj = HospitalsPerTenThousandResidents__Hospitals()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_impervious_area__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'impervious_area__percent.csv')

    metric_obj = ImperviousArea__Percent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_impervious_surface_on_urbanized_land__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'impervious_surface_on_urbanized_land__percent.csv')

    metric_obj = ImperviousSurfaceOnUrbanizedLand__Percent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_land_near_natural_drainage__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'land_near_natural_drainage__percent.csv')

    metric_obj = LandNearNaturalDrainage__Percent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure__microgramspercubicmeter(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'mean_pm2p5_exposure__microgramspercubicmeter.csv')

    metric_obj = MeanPM2P5Exposure__MicrogramsPerCubicMeter()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure_pop_weighted_children__microgramspercubicmeter(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'mean_pm2p5_exposure_pop_weighted_children__microgramspercubicmeter.csv')

    metric_obj = MeanPM2P5ExposurePopWeightedChildren__MicrogramsPerCubicMeter()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure_pop_weighted_elderly__microgramspercubicmeter(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'mean_pm2p5_exposure_pop_weighted_elderly__microgramspercubicmeter.csv')

    metric_obj = MeanPM2P5ExposurePopWeightedElderly__MicrogramsPerCubicMeter()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure_pop_weighted_female__microgramspercubicmeter(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'mean_pm2p5_exposure_pop_weighted_female__microgramspercubicmeter.csv')

    metric_obj = MeanPM2P5ExposurePopWeightedFemale__MicrogramsPerCubicMeter()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure_pop_weighted_informal__microgramspercubicmeter(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'mean_pm2p5_exposure_pop_weighted_informal__microgramspercubicmeter.csv')

    metric_obj = MeanPM2P5ExposurePopWeightedInformal__MicrogramsPerCubicMeter()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_tree_cover__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'mean_tree_cover__percent.csv')

    metric_obj = MeanTreeCover__Percent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_natural_areas__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'natural_areas__percent.csv')

    metric_obj = NaturalAreas__Percent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_number_species_bird_richness__species(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'bird_richness__species.csv')

    metric_obj = BirdRichness__Species()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_number_species_arthropod_richness__species(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'arthropod_richness__species.csv')

    metric_obj = ArthropodRichness__Species()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_number_species_vascular_plant_richness__species(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'vascular_plant_richness__species.csv')

    metric_obj = VascularPlantRichness__Species()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_number_species_bird_richness_in_builtup_area__species(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'bird_richness_in_builtup_area__species.csv')

    metric_obj = BirdRichnessInBuiltUpArea__Species()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_protected_area__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'protected_area__percent.csv')

    metric_obj = ProtectedArea__Percent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_recreational_space_per_thousand__hectaresperthousandpersons(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'recreational_space_per_thousand__hectaresperthousandpersons.csv')

    metric_obj = RecreationalSpacePerThousand__HectaresPerThousandPersons()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_riparian_land_with_vegetation_or_water__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'riparian_land_with_vegetation_or_water__percent.csv')

    metric_obj = RiparianLandWithVegetationOrWater__Percent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_riverine_or_coastal_flood_risk_area__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'riverine_or_coastal_flood_risk_area__percent.csv')

    metric_obj = RiverineOrCoastalFloodRiskArea__Percent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_steeply_sloped_land_with_vegetation__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'steeply_sloped_land_with_vegetation__percent.csv')

    metric_obj = SteeplySlopedLandWithVegetation__Percent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_tree_carbon_flux__tonnes(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'tree_carbon_flix__tonnes.csv')

    metric_obj = TreeCarbonFlux__Tonnes()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_urban_open_space__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'urban_open_space__percent.csv')

    metric_obj = UrbanOpenSpace__Percent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_vegetation_water_change_gain_area__squaremeters(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'vegetation_water_change_gain_area__squaremeters.csv')

    metric_obj = VegetationWaterChangeGainArea__SquareMeters()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_vegetation_water_change_loss_area__squaremeters(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'vegetation_water_change_loss_area__squaremeters.csv')

    metric_obj = VegetationWaterChangeLossArea__SquareMeters()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_vegetation_water_change_gain_loss__ratio(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'vegetation_water_change_gain_loss__ratio.csv')

    metric_obj = VegetationWaterChangeGainLoss__Ratio()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_water_cover__percent(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(
        target_folder, 'metric', 'water_cover__percent.csv')

    metric_obj = WaterCover__Percent()
    _write_verify(metric_obj, zones, file_path)


def _write_verify(metric_obj, zones, file_path):
    metric_obj.write(geo_zone=zones, target_file_path=file_path)
    assert verify_file_is_populated(file_path)
    if not PRESERVE_RESULTS_ON_OS:
        cleanup_cache_files(None, None, None, file_path)
