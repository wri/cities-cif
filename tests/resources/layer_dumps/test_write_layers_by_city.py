import os

import pytest

from city_metrix.constants import testing_aws_bucket, testing_s3_aws_profile
from city_metrix.layers import *
from city_metrix.layers.layer_dao import get_s3_layer_name, get_s3_file_key, get_s3_file_url, \
    get_s3_client, check_if_s3_file_exists, get_s3_variables
from city_metrix.layers.layer_tools import set_environment_variable
from .conftest import EXECUTE_IGNORED_TESTS, prep_output_path, verify_file_is_populated
from .tools import get_test_bbox
from ..bbox_constants import EXTENT_SMALL_CITY_WGS84, EXTENT_SMALL_CITY_UTM
from ...tools.general_tools import set_testing_environment_variables, clear_environment_variables


@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_esa_world_cover_os(target_folder):
    set_testing_environment_variables()
    file_path = prep_output_path(target_folder, 'esa_world_cover_small_city_wgs84.tif')
    bbox = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    EsaWorldCover(year=2020).write(bbox=bbox, output_path=file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_esa_world_cover_s3(target_folder):
    set_testing_environment_variables()
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    year = 2020
    query_layer = EsaWorldCover(year=year)
    file_key, file_url = get_s3_variables(geo_extent, query_layer, year)
    query_layer.write(bbox=geo_extent, output_path=file_url)
    s3_file_exists = check_if_s3_file_exists(get_s3_client(), file_key)
    assert s3_file_exists


@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_open_street_map_roads_s3(target_folder):
    set_testing_environment_variables()
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    road_features = OpenStreetMapClass.ROAD
    query_layer = OpenStreetMap(road_features)
    file_key, file_url = get_s3_variables(geo_extent, query_layer)
    query_layer.write(bbox=geo_extent, output_path=file_url)
    s3_file_exists = check_if_s3_file_exists(get_s3_client(), file_key)
    assert s3_file_exists


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



