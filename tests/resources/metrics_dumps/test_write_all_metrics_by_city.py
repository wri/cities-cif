import pytest
import timeout_decorator

from city_metrix.constants import DEFAULT_STAGING_ENV
from city_metrix.metrics import *
from city_metrix.cache_manager import check_if_cache_file_exists
from ...tools.general_tools import get_test_cache_variables
from ..bbox_constants import GEOZONE_TERESINA_WGS84, GEOEXTENT_TERESINA_WGS84, GEOEXTENT_FLORIANOPOLIS_WGS84, \
    GEOZONE_FLORIANOPOLIS_WGS84
from ..conftest import DUMP_RUN_LEVEL, DumpRunLevel
from ..tools import prep_output_path, cleanup_cache_files

PRESERVE_RESULTS_ON_OS = True  # False - Default for check-in

SLOW_TEST_TIMEOUT_SECONDS = 1500  # seconds


@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_BuiltLandWithHighLST(target_folder):
    metric_obj = BuiltLandWithHighLST()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_BuiltLandWithLowSurfaceReflectivity(target_folder):
    metric_obj = BuiltLandWithLowSurfaceReflectivity()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResident(target_folder):
    metric_obj = CanopyAreaPerResident()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResidentChildren(target_folder):
    metric_obj = CanopyAreaPerResidentChildren()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResidentElderly(target_folder):
    metric_obj = CanopyAreaPerResidentElderly()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResidentFemale(target_folder):
    metric_obj = CanopyAreaPerResidentFemale()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResidentInformal(target_folder):
    metric_obj = CanopyAreaPerResidentInformal()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_Era5MetPreprocessing(target_folder):
    metric_obj = Era5MetPreprocessing()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5Exposure(target_folder):
    metric_obj = MeanPM2P5Exposure()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5ExposurePopWeightedElderly(target_folder):
    metric_obj = MeanPM2P5ExposurePopWeightedElderly()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5ExposurePopWeightedFemale(target_folder):
    metric_obj = MeanPM2P5ExposurePopWeightedFemale()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5ExposurePopWeightedInformal(target_folder):
    metric_obj = MeanPM2P5ExposurePopWeightedInformal()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanTreeCover(target_folder):
    metric_obj = MeanTreeCover()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_NaturalAreasPercent(target_folder):
    metric_obj = NaturalAreasPercent()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_PercentAreaFracvegExceedsThreshold(target_folder):
    metric_obj = PercentAreaFracvegExceedsThreshold()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_PercentAreaImpervious(target_folder):
    metric_obj = PercentAreaImpervious()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_PercentBuiltAreaWithoutTreeCover(target_folder):
    metric_obj = PercentBuiltAreaWithoutTreeCover()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_PercentCanopyCoveredPopulation(target_folder):
    metric_obj = PercentCanopyCoveredPopulation()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_PercentProtectedArea(target_folder):
    metric_obj = PercentProtectedArea()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_RecreationalSpacePerCapita(target_folder):
    metric_obj = RecreationalSpacePerCapita()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_UrbanOpenSpace(target_folder):
    metric_obj = UrbanOpenSpace()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_VegetationWaterChangeGainArea(target_folder):
    metric_obj = VegetationWaterChangeGainArea()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_VegetationWaterChangeGainLossRatio(target_folder):
    metric_obj = VegetationWaterChangeGainLossRatio()
    _run_write_metrics_by_city_test(metric_obj, target_folder, GEOEXTENT_TERESINA_WGS84, GEOZONE_TERESINA_WGS84)


def _run_write_metrics_by_city_test(metric_obj, target_folder, geo_extent, geo_zone):
    cache_scheme = 's3'
    file_key, file_uri, metric_id, _ = get_test_cache_variables(metric_obj, geo_extent)

    os_file_path = prep_output_path(target_folder, 'metric', metric_id)
    try:
        # Do not force data refresh to avoid collisions with concurrent tests
        metric_obj.write(geo_zone=geo_zone, s3_env=DEFAULT_STAGING_ENV, force_data_refresh=True)
        cache_file_exists = check_if_cache_file_exists(file_uri)
        assert cache_file_exists, "Test failed since file did not upload to s3"
        if cache_file_exists and PRESERVE_RESULTS_ON_OS:
            metric_obj.write(geo_zone=geo_zone, s3_env=DEFAULT_STAGING_ENV, output_uri=os_file_path)
    finally:
        cleanup_os_file_path = None if PRESERVE_RESULTS_ON_OS else os_file_path
        # Note: Do not delete S3 files in order to avoid collisions with concurrent tests
