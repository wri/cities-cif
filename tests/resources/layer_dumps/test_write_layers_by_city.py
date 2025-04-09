import pytest

from city_metrix.file_cache_config import set_cache_settings
from city_metrix.constants import testing_aws_bucket_uri
from city_metrix.layers import *
from .tools import get_test_bbox
from ..bbox_constants import EXTENT_SMALL_CITY_WGS84, EXTENT_SMALL_CITY_UTM
from ..conftest import prep_output_path, DUMP_RUN_LEVEL, verify_file_is_populated, DumpRunLevel


@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_esa_world_cover_os(target_folder):
    set_cache_settings(testing_aws_bucket_uri, 'dev')
    file_path = prep_output_path(target_folder, 'esa_world_cover_small_city_wgs84.tif')
    bbox = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    subclass = EsaWorldCoverClass.BUILT_UP
    EsaWorldCover(land_cover_class=subclass, year=2020).write(bbox=bbox, output_path=file_path)


@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_nasa_dem(target_folder):
    set_cache_settings(testing_aws_bucket_uri, 'dev')
    file_path = prep_output_path(target_folder, 'nasa_dem_small_city_wgs84.tif')
    bbox = get_test_bbox(EXTENT_SMALL_CITY_WGS84)
    NasaDEM().write(bbox, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_nasa_dem_utm(target_folder):
    set_cache_settings(testing_aws_bucket_uri, 'dev')
    file_path = prep_output_path(target_folder, 'nasa_dem_small_city_utm.tif')
    bbox = get_test_bbox(EXTENT_SMALL_CITY_UTM)
    NasaDEM().write(bbox, file_path)
    assert verify_file_is_populated(file_path)
