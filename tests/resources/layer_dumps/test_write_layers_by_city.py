import pytest
from ..bbox_constants import EXTENT_SMALL_CITY_WGS84, EXTENT_SMALL_CITY_UTM
from city_metrix.layers import NasaDEM
from tests.resources.conftest import prep_output_path, verify_file_is_populated, EXECUTE_IGNORED_TESTS
from tests.resources.layer_dumps.tools import get_test_bbox


# Add back when API is stable
@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_nasa_dem(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'nasa_dem_small_city_wgs84.tif')
    bbox = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    NasaDEM().write(bbox, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_nasa_dem_utm(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'nasa_dem_small_city_utm.tif')
    bbox = get_test_bbox(EXTENT_SMALL_CITY_UTM)
    NasaDEM().write(bbox, file_path)
    assert verify_file_is_populated(file_path)

