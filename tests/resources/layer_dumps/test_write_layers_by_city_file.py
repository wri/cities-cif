import pytest

from city_metrix.config import set_cache_settings
from city_metrix.constants import testing_aws_bucket
from city_metrix.layers import *
from city_metrix.layers.layer_dao import get_cache_variables, check_if_cache_file_exists
from .conftest import EXECUTE_IGNORED_TESTS, prep_output_path, verify_file_is_populated
from .tools import get_test_bbox
from ..bbox_constants import EXTENT_SMALL_CITY_WGS84

import tempfile
temp_dir = tempfile.gettempdir()

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_AcagPM2p5_file(target_folder):
    set_cache_settings(f"file://{target_folder}", 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = AcagPM2p5()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_key)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)
