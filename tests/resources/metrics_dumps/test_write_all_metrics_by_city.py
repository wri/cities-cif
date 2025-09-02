import os

import pytest
import timeout_decorator

from city_metrix.constants import DEFAULT_DEVELOPMENT_ENV
from city_metrix.metrics import *
from city_metrix.cache_manager import check_if_cache_file_exists
from ...tools.general_tools import get_test_cache_variables
from ..bbox_constants import GEOZONE_TERESINA, GEOEXTENT_TERESINA
from ..conftest import DUMP_RUN_LEVEL, DumpRunLevel
from ..tools import prep_output_path, cleanup_cache_files

PRESERVE_RESULTS_ON_OS = False  # False - Default for check-in
OUTPUT_RESULTS_FORMAT = 'csv' # Default for check-in
# OUTPUT_RESULTS_FORMAT = 'geojson'

SLOW_TEST_TIMEOUT_SECONDS = 3600 # seconds = 1 hour (Duration needed for fractional vegetation)


@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_AreaFractionalVegetationExceedsThreshold__Percent(target_folder):
    metric_obj = AreaFractionalVegetationExceedsThreshold__Percent()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_BuiltLandWithHighLST(target_folder):
    metric_obj = BuiltLandWithHighLST()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_BuiltLandWithLowSurfaceReflectivity(target_folder):
    metric_obj = BuiltLandWithLowSurfaceReflectivity()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_BuiltLandWithVegetation__Percent(target_folder):
    metric_obj = BuiltLandWithVegetation__Percent()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResident(target_folder):
    metric_obj = CanopyAreaPerResident()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResidentChildren(target_folder):
    metric_obj = CanopyAreaPerResidentChildren()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResidentElderly(target_folder):
    metric_obj = CanopyAreaPerResidentElderly()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResidentFemale(target_folder):
    metric_obj = CanopyAreaPerResidentFemale()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResidentInformal(target_folder):
    metric_obj = CanopyAreaPerResidentInformal()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_Era5MetPreprocessingUmep(target_folder):
    metric_obj = Era5MetPreprocessingUmep(start_date='2023-01-01', end_date='2023-12-31', seasonal_utc_offset=-3)
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_HabitatTypesRestored__CoverTypes(target_folder):
    metric_obj = HabitatTypesRestored__CoverTypes()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_HospitalsPerTenThousandResidents(target_folder):
    metric_obj = HospitalsPerTenThousandResidents()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_ImperviousSurfaceOnUrbanizedLand__Percent(target_folder):
    metric_obj = ImperviousSurfaceOnUrbanizedLand__Percent()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_LandNearNaturalDrainage__Percent(target_folder):
    metric_obj = LandNearNaturalDrainage__Percent()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5Exposure(target_folder):
    metric_obj = MeanPM2P5Exposure()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5ExposurePopWeighted(target_folder):
    metric_obj = MeanPM2P5ExposurePopWeighted()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5ExposurePopWeightedElderly(target_folder):
    metric_obj = MeanPM2P5ExposurePopWeightedElderly()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5ExposurePopWeightedFemale(target_folder):
    metric_obj = MeanPM2P5ExposurePopWeightedFemale()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5ExposurePopWeightedInformal(target_folder):
    metric_obj = MeanPM2P5ExposurePopWeightedInformal()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanTreeCover__Percent(target_folder):
    metric_obj = MeanTreeCover__Percent()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_NaturalAreas__Percent(target_folder):
    metric_obj = NaturalAreas__Percent()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_number_species_BirdRichness__Species(target_folder):
    metric_obj = BirdRichness__Species()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_number_species_ArthropodRichness__Species(target_folder):
    metric_obj = ArthropodRichness__Species()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_number_species_VascularPlantRichness__Species(target_folder):
    metric_obj = VascularPlantRichness__Species()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_number_species_BirdRichnessInBuiltUpArea__Species(target_folder):
    metric_obj = BirdRichnessInBuiltUpArea__Species()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_PercentAreaImpervious(target_folder):
    metric_obj = PercentAreaImpervious()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_PercentBuiltAreaWithoutTreeCover(target_folder):
    metric_obj = PercentBuiltAreaWithoutTreeCover()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_PercentCanopyCoveredPopulation(target_folder):
    metric_obj = PercentCanopyCoveredPopulation()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_PercentProtectedArea(target_folder):
    metric_obj = PercentProtectedArea()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_RecreationalSpacePerCapita(target_folder):
    metric_obj = RecreationalSpacePerCapita()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_RiparianLandWithVegatationOrWater__Percent(target_folder):
    metric_obj = RiparianLandWithVegetationOrWater__Percent()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_RiverineOrCoastalFloodRiskArea__Percent(target_folder):
    metric_obj = RiverineOrCoastalFloodRiskArea__Percent()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_SteeplySlopedLandWithVegatation__Percent(target_folder):
    metric_obj = SteeplySlopedLandWithVegetation__Percent()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_TreeCarbonFlux__Tonnes(target_folder):
    metric_obj = TreeCarbonFlux__Tonnes()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_UrbanOpenSpace(target_folder):
    metric_obj = UrbanOpenSpace()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_VegetationWaterChangeGainArea(target_folder):
    metric_obj = VegetationWaterChangeGainArea()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_VegetationWaterChangeGainLossRatio(target_folder):
    metric_obj = VegetationWaterChangeGainLossRatio()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_WaterCover__Percent(target_folder):
    metric_obj = WaterCover__Percent()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA, GEOZONE_TERESINA)


def _run_write_metrics_by_city_test(metric_obj, target_folder, geo_extent, geo_zone):
    file_key, file_uri, metric_id, _ = get_test_cache_variables(metric_obj, geo_extent)
    metric_geojson_path = '/tmp/test_result_tif_files/metric_geojson'

    os_file_path = None
    try:
        if OUTPUT_RESULTS_FORMAT == 'csv':
            os_file_path = prep_output_path(target_folder, 'metric', metric_id)
            metric_obj.write(geo_zone=geo_zone, s3_env=DEFAULT_DEVELOPMENT_ENV, output_uri=os_file_path,
                             force_data_refresh=True)
            cache_file_exists = check_if_cache_file_exists(file_uri)
        else:
            metric_name = metric_obj.__class__.__name__
            os_file_path = f'{metric_geojson_path}/{metric_name}.geojson'
            metric_obj.write_as_geojson(geo_zone=geo_zone, s3_env=DEFAULT_DEVELOPMENT_ENV, output_uri=os_file_path,
                                        force_data_refresh=True)
            cache_file_exists = check_if_cache_file_exists(file_uri)

        assert cache_file_exists, "Test failed since file did not upload to s3"
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
