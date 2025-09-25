import os
import tempfile
import pytest
import timeout_decorator

from city_metrix.constants import DEFAULT_DEVELOPMENT_ENV, CIF_TESTING_S3_BUCKET_URI
from city_metrix.metrics import *
from city_metrix.cache_manager import is_cache_object_available
from ...tools.general_tools import get_test_cache_variables
from ..bbox_constants import GEOZONE_TERESINA, GEOEXTENT_TERESINA
from ..conftest import DUMP_RUN_LEVEL, DumpRunLevel
from ..tools import prep_output_path, cleanup_cache_files, verify_file_is_populated

PRESERVE_RESULTS_ON_OS = False  # False - Default for check-in
OUTPUT_RESULTS_FORMAT = 'csv'  # Default for check-in
# OUTPUT_RESULTS_FORMAT = 'geojson'

# seconds = 1 hour (Duration needed for fractional vegetation)
SLOW_TEST_TIMEOUT_SECONDS = 3600

TEST_BUCKET = CIF_TESTING_S3_BUCKET_URI # Default for testing
S3_ENV=DEFAULT_DEVELOPMENT_ENV

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_AreaFractionalVegetationExceedsThreshold__Percent(target_folder):
    metric_obj = AreaFractionalVegetationExceedsThreshold__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_BuiltAreaWithoutTreeCover__Percent(target_folder):
    metric_obj = BuiltAreaWithoutTreeCover__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_BuiltLandWithHighLST__Percent(target_folder):
    metric_obj = BuiltLandWithHighLST__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_BuiltLandWithLowSurfaceReflectivity__Percent(target_folder):
    metric_obj = BuiltLandWithLowSurfaceReflectivity__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_BuiltLandWithVegetation__Percent(target_folder):
    metric_obj = BuiltLandWithVegetation__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResident__SquareMeters(target_folder):
    metric_obj = CanopyAreaPerResident__SquareMeters()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResidentChildren__SquareMeters(target_folder):
    metric_obj = CanopyAreaPerResidentChildren__SquareMeters()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResidentElderly__SquareMeters(target_folder):
    metric_obj = CanopyAreaPerResidentElderly__SquareMeters()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResidentFemale__SquareMeters(target_folder):
    metric_obj = CanopyAreaPerResidentFemale__SquareMeters()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResidentInformal__SquareMeters(target_folder):
    metric_obj = CanopyAreaPerResidentInformal__SquareMeters()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyCoveredPopulation__Percent(target_folder):
    metric_obj = CanopyCoveredPopulation__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_Era5MetPreprocessingUmep(target_folder):
    metric_obj = Era5MetPreprocessingUmep(
        start_date='2023-01-01', end_date='2023-12-31', seasonal_utc_offset=-3)
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_GhgEmissions__Tonnes(target_folder):
    metric_obj = GhgEmissions__Tonnes()

def test_write_HabitatConnectivityCoherence__Percent(target_folder):
    metric_obj = HabitatConnectivityCoherence__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_HabitatConnectivityEffectiveMeshSize__Hectares(target_folder):
    metric_obj = HabitatConnectivityEffectiveMeshSize__Hectares()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_HabitatTypesRestored__CoverTypes(target_folder):
    metric_obj = HabitatTypesRestored__CoverTypes()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_HospitalsPerTenThousandResidents__Hospitals(target_folder):
    metric_obj = HospitalsPerTenThousandResidents__Hospitals()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_ImperviousArea__Percent(target_folder):
    metric_obj = ImperviousArea__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_ImperviousSurfaceOnUrbanizedLand__Percent(target_folder):
    metric_obj = ImperviousSurfaceOnUrbanizedLand__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_KeyBiodiversityAreaProtected__Percent(target_folder):
    metric_obj = KeyBiodiversityAreaProtected__Percent()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_KeyBiodiversityAreaUndeveloped__Percent(target_folder):
    metric_obj = KeyBiodiversityAreaUndeveloped__Percent()

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_LandNearNaturalDrainage__Percent(target_folder):
    metric_obj = LandNearNaturalDrainage__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5Exposure__MicrogramsPerCubicMeter(target_folder):
    metric_obj = MeanPM2P5Exposure__MicrogramsPerCubicMeter()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5ExposurePopWeighted__MicrogramsPerCubicMeter(target_folder):
    metric_obj = MeanPM2P5ExposurePopWeighted__MicrogramsPerCubicMeter()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5ExposurePopWeightedElderly__MicrogramsPerCubicMeter(target_folder):
    metric_obj = MeanPM2P5ExposurePopWeightedElderly__MicrogramsPerCubicMeter()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5ExposurePopWeightedFemale__MicrogramsPerCubicMeter(target_folder):
    metric_obj = MeanPM2P5ExposurePopWeightedFemale__MicrogramsPerCubicMeter()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5ExposurePopWeightedInformal__MicrogramsPerCubicMeter(target_folder):
    metric_obj = MeanPM2P5ExposurePopWeightedInformal__MicrogramsPerCubicMeter()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanTreeCover__Percent(target_folder):
    metric_obj = MeanTreeCover__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_NaturalAreas__Percent(target_folder):
    metric_obj = NaturalAreas__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_number_species_BirdRichness__Species(target_folder):
    metric_obj = BirdRichness__Species()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_number_species_ArthropodRichness__Species(target_folder):
    metric_obj = ArthropodRichness__Species()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_number_species_VascularPlantRichness__Species(target_folder):
    metric_obj = VascularPlantRichness__Species()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_number_species_BirdRichnessInBuiltUpArea__Species(target_folder):
    metric_obj = BirdRichnessInBuiltUpArea__Species()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_ProtectedArea__Percent(target_folder):
    metric_obj = ProtectedArea__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_RecreationalSpacePerThousand__HectaresPerThousandPersons(target_folder):
    metric_obj = RecreationalSpacePerThousand__HectaresPerThousandPersons()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_RiparianLandWithVegatationOrWater__Percent(target_folder):
    metric_obj = RiparianLandWithVegetationOrWater__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_RiverineOrCoastalFloodRiskArea__Percent(target_folder):
    metric_obj = RiverineOrCoastalFloodRiskArea__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_SteeplySlopedLandWithVegatation__Percent(target_folder):
    metric_obj = SteeplySlopedLandWithVegetation__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_TreeCarbonFlux__Tonnes(target_folder):
    metric_obj = TreeCarbonFlux__Tonnes()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_UrbanOpenSpace__Percent(target_folder):
    metric_obj = UrbanOpenSpace__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_VegetationWaterChangeGainArea__SquareMeters(target_folder):
    metric_obj = VegetationWaterChangeGainArea__SquareMeters()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_VegetationWaterChangeGainLoss__Ratio(target_folder):
    metric_obj = VegetationWaterChangeGainLoss__Ratio()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_WaterCover__Percent(target_folder):
    metric_obj = WaterCover__Percent()
    _run_write_metrics_by_city_test(
        metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)


def _run_write_metrics_by_city_test(metric_obj, target_folder, geo_extent, geo_zone):
    _, _, metric_id, _ = get_test_cache_variables(metric_obj, geo_extent, CIF_TESTING_S3_BUCKET_URI)
    temp_dir = tempfile.gettempdir()
    metric_geojson_path = os.path.join(temp_dir, 'test_result_tif_files', 'metric_geojson')

    os_file_path = None
    try:
        if OUTPUT_RESULTS_FORMAT == 'csv':
            os_file_path = prep_output_path(target_folder, 'metric', metric_id)
            metric_obj.write(geo_zone=geo_zone, s3_bucket=TEST_BUCKET, s3_env=S3_ENV, target_file_path=os_file_path)
            file_exists = verify_file_is_populated(os_file_path)
        else:
            metric_name = metric_obj.__class__.__name__
            os_file_path = os.path.join(metric_geojson_path, f'{metric_name}.geojson')
            metric_obj.write_as_geojson(geo_zone=geo_zone, s3_bucket=TEST_BUCKET, s3_env=S3_ENV, target_file_path=os_file_path)
            file_exists = verify_file_is_populated(os_file_path)

        assert file_exists, "Test failed since file did not upload to s3"
    finally:
        if PRESERVE_RESULTS_ON_OS and OUTPUT_RESULTS_FORMAT == 'geojson':
            import shutil
            viewer_name = '_metrics_viewer.qgz'
            application_path = os.path.dirname(os.path.abspath(__file__))
            source_viewer_path = os.path.join(application_path, viewer_name)
            target_viewer_path = os.path.join(metric_geojson_path, viewer_name)
            shutil.copy(source_viewer_path, target_viewer_path)

        # Note: Do not delete S3 files in order to avoid collisions with concurrent tests
        cleanup_os_file_path = None if PRESERVE_RESULTS_ON_OS else os_file_path
        cleanup_cache_files('layer', None, None, cleanup_os_file_path)
