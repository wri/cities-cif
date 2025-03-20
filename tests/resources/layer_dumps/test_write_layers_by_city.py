import os

import pytest

from city_metrix.constants import testing_aws_bucket, testing_s3_aws_profile
from city_metrix.layers import *
from city_metrix.layers.layer_dao import set_environment_variable, get_s3_layer_name, get_s3_file_key, get_s3_file_url, \
    get_s3_client, check_if_s3_file_exists
from .conftest import EXECUTE_IGNORED_TESTS, prep_output_path, verify_file_is_populated
from .tools import get_test_bbox
from ..bbox_constants import EXTENT_SMALL_CITY_WGS84, EXTENT_SMALL_CITY_UTM

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_esa_world_cover_os(target_folder):
    file_path = prep_output_path(target_folder, 'esa_world_cover_small_city_wgs84.tif')
    bbox = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    EsaWorldCover(year=2020).write(bbox=bbox, output_path=file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_esa_world_cover_s3(target_folder):
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    year = 2020
    query_layer = EsaWorldCover(year=year)
    try:
        set_environment_variable('AWS_BUCKET', testing_aws_bucket)
        set_environment_variable('S3_AWS_PROFILE', testing_s3_aws_profile)

        city_id = geo_extent.city_id
        admin_level = geo_extent.admin_level
        layer_id = query_layer.LAYER_ID
        file_format = query_layer.OUTPUT_FILE_FORMAT
        file_name = get_s3_layer_name(city_id, admin_level, layer_id, year, file_format)
        file_key = get_s3_file_key(city_id, file_format, file_name)
        file_url = get_s3_file_url(file_key)
        query_layer.write(bbox=geo_extent, output_path=file_url)

        s3_client = get_s3_client()
        s3_file_exists = check_if_s3_file_exists(s3_client, file_key)
    finally:
        set_environment_variable('AWS_BUCKET', '')
        set_environment_variable('S3_AWS_PROFILE', '')

    assert s3_file_exists



@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_nasa_dem(target_folder):
    file_path = prep_output_path(target_folder, 'nasa_dem_small_city_wgs84.tif')
    bbox = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    NasaDEM().write(bbox, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_nasa_dem_utm(target_folder):
    file_path = prep_output_path(target_folder, 'nasa_dem_small_city_utm.tif')
    bbox = get_test_bbox(EXTENT_SMALL_CITY_UTM)
    NasaDEM().write(bbox, file_path)
    assert verify_file_is_populated(file_path)
