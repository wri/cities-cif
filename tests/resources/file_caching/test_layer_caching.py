import numpy as np
import pytest

from city_metrix.constants import CIF_TESTING_S3_BUCKET_URI, DEFAULT_DEVELOPMENT_ENV
from city_metrix.layers import AcagPM2p5, Era5HottestDay, UrbanExtents, OpenStreetMapClass, OpenStreetMap
from city_metrix.cache_manager import is_cache_object_available
from tests.resources.conftest import DUMP_RUN_LEVEL, DumpRunLevel
from tests.tools.general_tools import get_test_cache_variables
from tests.resources.bbox_constants import GEOEXTENT_TERESINA

TEST_BUCKET = CIF_TESTING_S3_BUCKET_URI

GEO_EXTENT_PROCESSING_CITY = GEOEXTENT_TERESINA
CITY_UT_NAME = 'teresina'


@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_geojson_default_param_vals():
    layer_obj = UrbanExtents()
    is_custom_layer = _run_cache_test(layer_obj)
    assert is_custom_layer == False

# TODO - There currently are no custom layer options. Find one later, such as ProtectedAreas that actually returns features
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_geojson_custom_param_val():
    layer_obj = OpenStreetMap(osm_class=OpenStreetMapClass.MEDICAL)
    is_custom_layer = _run_cache_test(layer_obj)
    assert is_custom_layer == False

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_geotiff_default_param_val():
    layer_obj = AcagPM2p5()
    is_custom_layer = _run_cache_test(layer_obj)
    assert is_custom_layer == False

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_geotiff_custom_param_val():
    layer_obj = AcagPM2p5(return_above=1)
    is_custom_layer = _run_cache_test(layer_obj)
    assert is_custom_layer == True

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_netcdf_default_param_val():
    layer_obj = Era5HottestDay(start_date='2023-01-01', end_date='2023-12-31', seasonal_utc_offset=-8)
    is_custom_layer = _run_cache_test(layer_obj)
    assert is_custom_layer == True


def _run_cache_test(layer_obj):
    _, file_uri, _, is_custom_layer = get_test_cache_variables(layer_obj, GEO_EXTENT_PROCESSING_CITY, TEST_BUCKET)

    data = layer_obj.cache_city_data(bbox=GEO_EXTENT_PROCESSING_CITY, s3_bucket=TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, force_data_refresh=True)
    assert np.size(data) > 0

    cache_file_exists = is_cache_object_available(file_uri)
    assert cache_file_exists

    return is_custom_layer
