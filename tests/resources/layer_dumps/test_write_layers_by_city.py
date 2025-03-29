import pytest

from city_metrix.layers import *
from .conftest import EXECUTE_IGNORED_TESTS, prep_output_path, verify_file_is_populated
from .tools import get_test_bbox
from ..bbox_constants import EXTENT_SMALL_CITY_WGS84, EXTENT_SMALL_CITY_UTM
from ...tools.general_tools import set_testing_environment_variables, clear_environment_variables


@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_esa_world_cover_os(target_folder):
    set_testing_environment_variables()
    file_path = prep_output_path(target_folder, 'esa_world_cover_small_city_wgs84.tif')
    bbox = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    subclass = EsaWorldCoverClass.BUILT_UP
    EsaWorldCover(land_cover_class=subclass, year=2020).write(bbox=bbox, output_path=file_path)


@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_nasa_dem(target_folder):
    set_testing_environment_variables()
    file_path = prep_output_path(target_folder, 'nasa_dem_small_city_wgs84.tif')
    bbox = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    NasaDEM().write(bbox, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_nasa_dem_utm(target_folder):
    set_testing_environment_variables()
    file_path = prep_output_path(target_folder, 'nasa_dem_small_city_utm.tif')
    bbox = get_test_bbox(EXTENT_SMALL_CITY_UTM)
    NasaDEM().write(bbox, file_path)
    assert verify_file_is_populated(file_path)



