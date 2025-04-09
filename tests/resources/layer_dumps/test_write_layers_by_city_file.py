import pytest

from city_metrix.file_cache_config import set_cache_settings
from city_metrix.layers import *
from city_metrix.layers.layer_dao import get_cache_variables, check_if_cache_file_exists
from .tools import get_test_bbox, delete_file_on_os
from ..bbox_constants import EXTENT_SMALL_CITY_WGS84
from ..conftest import EXECUTE_IGNORED_TESTS, prep_output_path, verify_file_is_populated

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_AcagPM2p5_file(target_folder):
    set_cache_settings(f"file://{target_folder}", 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = AcagPM2p5()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)

    delete_file_on_os(file_uri)
    layer_obj.write(bbox=geo_extent, output_path=file_uri)
    cache_file_exists = check_if_cache_file_exists(file_uri)
    assert cache_file_exists, "Test failed since file did not upload to cache"
    if cache_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)
    delete_file_on_os(file_uri)
