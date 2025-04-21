import pytest
import timeout_decorator

from city_metrix.metrics import *
from city_metrix.cache_manager import check_if_cache_file_exists
from ...tools.general_tools import get_layer_cache_variables
from ..bbox_constants import GEOZONE_TERESINA_WGS84, GEOEXTENT_TERESINA_WGS84
from ..conftest import DUMP_RUN_LEVEL, DumpRunLevel
from ..tools import prep_output_path, cleanup_cache_files

PRESERVE_RESULTS_ON_S3 = True # True - Default for check-in
PRESERVE_RESULTS_ON_OS = False # False - Default for check-in
FORCE_DATA_REFRESH = False # False - Default for check-in
SLOW_TEST_TIMEOUT_SECONDS = 60 # 1 minute

PROCESSING_CITY = GEOEXTENT_TERESINA_WGS84
PROCESSING_CITY_GEOZONE = GEOZONE_TERESINA_WGS84
CITY_UT_NAME = 'teresina'

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_BuiltLandWithHighLST(target_folder):
    metric_obj = BuiltLandWithHighLST()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_BuiltLandWithLowSurfaceReflectivity(target_folder):
    metric_obj = BuiltLandWithLowSurfaceReflectivity()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_BuiltLandWithoutTreeCover(target_folder):
    metric_obj = BuiltLandWithoutTreeCover()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResidentChildren(target_folder):
    metric_obj = CanopyAreaPerResidentChildren()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResidentElderly(target_folder):
    metric_obj = CanopyAreaPerResidentElderly()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResidentFemale(target_folder):
    metric_obj = CanopyAreaPerResidentFemale()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_CanopyAreaPerResidentInformal(target_folder):
    metric_obj = CanopyAreaPerResidentInformal()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_Era5MetPreprocessing(target_folder):
    metric_obj = Era5MetPreprocessing()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5Exposure(target_folder):
    metric_obj = MeanPM2P5Exposure()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5ExposurePopWeightedElderly(target_folder):
    metric_obj = MeanPM2P5ExposurePopWeightedElderly()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5ExposurePopWeightedFemale(target_folder):
    metric_obj = MeanPM2P5ExposurePopWeightedFemale()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanPM2P5ExposurePopWeightedInformal(target_folder):
    metric_obj = MeanPM2P5ExposurePopWeightedInformal()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_MeanTreeCover(target_folder):
    metric_obj = MeanTreeCover()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_NaturalAreasPercent(target_folder):
    metric_obj = NaturalAreasPercent()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_PercentAreaFracvegExceedsThreshold(target_folder):
    metric_obj = PercentAreaFracvegExceedsThreshold()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_PercentAreaImpervious(target_folder):
    metric_obj = PercentAreaImpervious()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_PercentCanopyCoveredPopulation(target_folder):
    metric_obj = PercentCanopyCoveredPopulation()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_PercentProtectedArea(target_folder):
    metric_obj = PercentProtectedArea()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_RecreationalSpacePerCapita(target_folder):
    metric_obj = RecreationalSpacePerCapita()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_UrbanOpenSpace(target_folder):
    metric_obj = UrbanOpenSpace()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_VegetationWaterChangeGainArea(target_folder):
    metric_obj = VegetationWaterChangeGainArea()
    _run_write_metrics_by_city_test(metric_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_VegetationWaterChangeGainLossRatio(target_folder):
    metric_obj = VegetationWaterChangeGainLossRatio()
    _run_write_metrics_by_city_test(metric_obj, target_folder)


def _run_write_metrics_by_city_test(metric_obj, target_folder):
    geo_zone = PROCESSING_CITY_GEOZONE
    file_key, file_uri, metric_id, _ = get_layer_cache_variables(metric_obj, PROCESSING_CITY)

    os_file_path = prep_output_path(target_folder, 'metric', metric_id)
    try:
        metric_obj.write(geo_zone=geo_zone, output_path=file_uri, force_data_refresh=FORCE_DATA_REFRESH)
        cache_file_exists = check_if_cache_file_exists(file_uri)
        assert cache_file_exists, "Test failed since file did not upload to s3"
        if cache_file_exists and PRESERVE_RESULTS_ON_OS:
            metric_obj.write(geo_zone=geo_zone, output_path=os_file_path)
    finally:
        cleanup_os_file_path = None if PRESERVE_RESULTS_ON_OS else os_file_path
        file_key = None if PRESERVE_RESULTS_ON_S3 else file_key
        cleanup_cache_files('s3', file_key, cleanup_os_file_path)
    