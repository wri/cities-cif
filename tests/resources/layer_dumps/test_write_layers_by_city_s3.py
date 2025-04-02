import pytest

from city_metrix.config import set_cache_settings
from city_metrix.constants import testing_aws_bucket
from city_metrix.layers import *
from city_metrix.layers.layer_dao import get_cache_variables, check_if_cache_file_exists
from .conftest import EXECUTE_IGNORED_TESTS, prep_output_path, verify_file_is_populated
from .tools import get_test_bbox
from ..bbox_constants import EXTENT_SMALL_CITY_WGS84


@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_AcagPM2p5_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = AcagPM2p5()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_Albedo_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = Albedo(start_date='2021-01-01', end_date='2021-12-31')
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_AlosDSM_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = AlosDSM()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_AqueductFlood_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = AqueductFlood()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_AverageNetBuildingHeight_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = AverageNetBuildingHeight()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_BuiltUpHeight_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = BuiltUpHeight()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_EsaWorldCover_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = EsaWorldCover(year=2020)
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_EsaWorldCover_built_up_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP,year=2020)
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)


@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_HeightAboveNearestDrainage_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = HeightAboveNearestDrainage()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_HighLandSurfaceTemperature_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = HighLandSurfaceTemperature()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_HighSlope_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = HighSlope()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_ImperviousSurface_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = ImperviousSurface()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
# def test_LandCoverGlad_s3(target_folder):
#     set_cache_settings(testing_aws_bucket, 'dev')
#     geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
#     layer_obj = LandCoverGlad(year=2020)
#     file_key, file_uri, layer_id = get_s3_variables(layer_obj, geo_extent)
#     s3_file_exists = check_if_s3_file_exists(file_key)
#     if not s3_file_exists:
#         layer_obj.write(bbox=geo_extent, output_path=file_uri)
#         s3_file_exists = check_if_s3_file_exists(file_key)
#         assert s3_file_exists, "Test failed since file did not upload to s3"
#     if s3_file_exists:
#         file_path = prep_output_path(target_folder, layer_id)
#         layer_obj.write(bbox=geo_extent, output_path=file_path)
#         assert verify_file_is_populated(file_path)

# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
# def test_LandCoverSimplifiedGlad_s3(target_folder):
#     set_cache_settings(testing_aws_bucket, 'dev')
#     geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
#     layer_obj = LandCoverSimplifiedGlad(year=2020)
#     file_key, file_uri, layer_id = get_s3_variables(layer_obj, geo_extent)
#     s3_file_exists = check_if_s3_file_exists(file_key)
#     if not s3_file_exists:
#         layer_obj.write(bbox=geo_extent, output_path=file_uri)
#         s3_file_exists = check_if_s3_file_exists(file_key)
#         assert s3_file_exists, "Test failed since file did not upload to s3"
#     if s3_file_exists:
#         file_path = prep_output_path(target_folder, layer_id)
#         layer_obj.write(bbox=geo_extent, output_path=file_path)
#         assert verify_file_is_populated(file_path)
#
# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
# def test_LandCoverHabitatGlad_s3(target_folder):
#     set_cache_settings(testing_aws_bucket, 'dev')
#     geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
#     layer_obj = LandCoverHabitatGlad(year=2020)
#     file_key, file_uri, layer_id = get_s3_variables(layer_obj, geo_extent)
#     s3_file_exists = check_if_s3_file_exists(file_key)
#     if not s3_file_exists:
#         layer_obj.write(bbox=geo_extent, output_path=file_uri)
#         s3_file_exists = check_if_s3_file_exists(file_key)
#         assert s3_file_exists, "Test failed since file did not upload to s3"
#     if s3_file_exists:
#         file_path = prep_output_path(target_folder, layer_id)
#         layer_obj.write(bbox=geo_extent, output_path=file_path)
#         assert verify_file_is_populated(file_path)
#
# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
# def test_LandCoverHabitatChangeGlad_s3(target_folder):
#     set_cache_settings(testing_aws_bucket, 'dev')
#     geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
#     layer_obj = LandCoverHabitatChangeGlad(start_year=2000, end_year=2020)
#     file_key, file_uri, layer_id = get_s3_variables(layer_obj, geo_extent)
#     s3_file_exists = check_if_s3_file_exists(file_key)
#     if not s3_file_exists:
#         layer_obj.write(bbox=geo_extent, output_path=file_uri)
#         s3_file_exists = check_if_s3_file_exists(file_key)
#         assert s3_file_exists, "Test failed since file did not upload to s3"
#     if s3_file_exists:
#         file_path = prep_output_path(target_folder, layer_id)
#         layer_obj.write(bbox=geo_extent, output_path=file_path)
#         assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_LandSurfaceTemperature_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = LandSurfaceTemperature(start_date='2022-01-01', end_date='2022-12-31')
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
# def test_LandsatCollection2_s3(target_folder):
#     set_cache_settings(testing_aws_bucket, 'dev')
#     geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
#     layer_obj = LandsatCollection2(bands=['blue'], start_date='2022-01-01', end_date='2022-12-31')
#     file_key, file_uri, layer_id = get_s3_variables(layer_obj, geo_extent)
#     s3_file_exists = check_if_s3_file_exists(file_key)
#     if not s3_file_exists:
#         layer_obj.write(bbox=geo_extent, output_path=file_uri)
#         s3_file_exists = check_if_s3_file_exists(file_key)
#         assert s3_file_exists, "Test failed since file did not upload to s3"
#     if s3_file_exists:
#         file_path = prep_output_path(target_folder, layer_id)
#         layer_obj.write(bbox=geo_extent, output_path=file_path)
#         assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_NasaDEM_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = NasaDEM()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_NaturalAreas_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = NaturalAreas()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_NdviSentinel2_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = NdviSentinel2(year=2020)
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_OpenBuildings_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = OpenBuildings()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_OpenStreetMap_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = OpenStreetMap(osm_class=OpenStreetMapClass.OPEN_SPACE)
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_OvertureBuildings_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = OvertureBuildings()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_PopWeightedPM2p5_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = PopWeightedPM2p5()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_ProtectedAreas_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = ProtectedAreas()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_RiparianAreas_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = RiparianAreas()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
# def test_Sentinel2Level2_s3(target_folder):
#     set_cache_settings(testing_aws_bucket, 'dev')
#     geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
#     layer_obj = Sentinel2Level2(bands=['blue'], start_date='2022-01-01', end_date='2022-12-31')
#     file_key, file_uri, layer_id = get_s3_variables(layer_obj, geo_extent)
#     s3_file_exists = check_if_s3_file_exists(file_key)
#     if not s3_file_exists:
#         layer_obj.write(bbox=geo_extent, output_path=file_uri)
#         s3_file_exists = check_if_s3_file_exists(file_key)
#         assert s3_file_exists, "Test failed since file did not upload to s3"
#     if s3_file_exists:
#         file_path = prep_output_path(target_folder, layer_id)
#         layer_obj.write(bbox=geo_extent, output_path=file_path)
#         assert verify_file_is_populated(file_path)

# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
# def test_SmartSurfaceLULC_s3(target_folder):
#     set_cache_settings(testing_aws_bucket, 'dev')
#     geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
#     layer_obj = SmartSurfaceLULC()
#     file_key, file_uri, layer_id = get_s3_variables(layer_obj, geo_extent)
#     s3_file_exists = check_if_s3_file_exists(file_key)
#     if not s3_file_exists:
#         layer_obj.write(bbox=geo_extent, output_path=file_uri)
#         s3_file_exists = check_if_s3_file_exists(file_key)
#         assert s3_file_exists, "Test failed since file did not upload to s3"
#     if s3_file_exists:
#         file_path = prep_output_path(target_folder, layer_id)
#         layer_obj.write(bbox=geo_extent, output_path=file_path)
#         assert verify_file_is_populated(file_path)

# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
# def test_TreeCanopyHeight_s3(target_folder):
#     set_cache_settings(testing_aws_bucket, 'dev')
#     geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
#     layer_obj = TreeCanopyHeight()
#     file_key, file_uri, layer_id = get_s3_variables(layer_obj, geo_extent)
#     s3_file_exists = check_if_s3_file_exists(file_key)
#     if not s3_file_exists:
#         layer_obj.write(bbox=geo_extent, output_path=file_uri)
#         s3_file_exists = check_if_s3_file_exists(file_key)
#         assert s3_file_exists, "Test failed since file did not upload to s3"
#     if s3_file_exists:
#         file_path = prep_output_path(target_folder, layer_id)
#         layer_obj.write(bbox=geo_extent, output_path=file_path)
#         assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_TreeCover_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = TreeCover()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_UrbanExtents_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = UrbanExtents(year=2020)
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_UrbanLandUse_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = UrbanLandUse()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)

# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
# def test_VegetationWaterMap_s3(target_folder):
#     set_cache_settings(testing_aws_bucket, 'dev')
#     geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
#     layer_obj = VegetationWaterMap(start_date='2020-01-01', end_date='2020-12-31')
#     file_key, file_uri, layer_id = get_s3_variables(layer_obj, geo_extent)
#     s3_file_exists = check_if_s3_file_exists(file_key)
#     if not s3_file_exists:
#         layer_obj.write(bbox=geo_extent, output_path=file_uri)
#         s3_file_exists = check_if_s3_file_exists(file_key)
#         assert s3_file_exists, "Test failed since file did not upload to s3"
#     if s3_file_exists:
#         file_path = prep_output_path(target_folder, layer_id)
#         layer_obj.write(bbox=geo_extent, output_path=file_path)
#         assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_WorldPop_s3(target_folder):
    set_cache_settings(testing_aws_bucket, 'dev')
    geo_extent = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    layer_obj = WorldPop()
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)
    s3_file_exists = check_if_cache_file_exists(file_uri)
    if not s3_file_exists:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        s3_file_exists = check_if_cache_file_exists(file_uri)
        assert s3_file_exists, "Test failed since file did not upload to s3"
    if s3_file_exists:
        file_path = prep_output_path(target_folder, layer_id)
        layer_obj.write(bbox=geo_extent, output_path=file_path)
        assert verify_file_is_populated(file_path)
