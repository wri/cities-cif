import numpy as np
import pytest

from city_metrix.constants import RW_TESTING_S3_BUCKET_URI, DEFAULT_DEVELOPMENT_ENV
from city_metrix.layers import AcagPM2p5, ProtectedAreas, Era5HottestDay
from city_metrix.cache_manager import check_if_cache_file_exists
from tests.resources.conftest import DUMP_RUN_LEVEL, DumpRunLevel
from tests.tools.general_tools import get_test_cache_variables
from tests.resources.bbox_constants import GEOEXTENT_TERESINA_WGS84

PROCESSING_CITY = GEOEXTENT_TERESINA_WGS84
CITY_UT_NAME = 'teresina'


@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_geojson_default_val():
    layer_obj = ProtectedAreas()
    is_custom_layer = _run_cache_test(layer_obj)
    assert is_custom_layer == False

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_geojson_default_variant_val():
    layer_obj = ProtectedAreas(status_year=2020)
    is_custom_layer = _run_cache_test(layer_obj)
    assert is_custom_layer == False

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_geojson_custom_val():
    layer_obj = ProtectedAreas(status=['Inscribed', 'Adopted', 'Designated'],status_year=2020)
    is_custom_layer = _run_cache_test(layer_obj)
    assert is_custom_layer == True

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_geotiff_default_val():
    layer_obj = AcagPM2p5()
    is_custom_layer = _run_cache_test(layer_obj)
    assert is_custom_layer == False

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_geotiff_custom_val():
    layer_obj = AcagPM2p5(return_above=1)
    is_custom_layer = _run_cache_test(layer_obj)
    assert is_custom_layer == True

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_netcdf_default_val():
    layer_obj = Era5HottestDay()
    is_custom_layer = _run_cache_test(layer_obj)
    assert is_custom_layer == False

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_netcdf_custom_val():
    layer_obj = Era5HottestDay(start_date="2023-02-01")
    is_custom_layer = _run_cache_test(layer_obj)
    assert is_custom_layer == True

def _run_cache_test(layer_obj):
    _, file_uri, _, is_custom_layer = get_test_cache_variables(layer_obj, PROCESSING_CITY)

    data = layer_obj.get_data_with_caching(bbox=PROCESSING_CITY, s3_env=DEFAULT_DEVELOPMENT_ENV, force_data_refresh=True)
    assert np.size(data) > 0

    cache_file_exists = check_if_cache_file_exists(file_uri)
    assert cache_file_exists

    return is_custom_layer
