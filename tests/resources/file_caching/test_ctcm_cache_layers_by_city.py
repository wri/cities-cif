import time
import pytest

from city_metrix import TreeCanopyHeight
from city_metrix.cache_manager import check_if_cache_object_exists
from city_metrix.constants import DEFAULT_DEVELOPMENT_ENV, CIF_TESTING_S3_BUCKET_URI
from city_metrix.layers import OvertureBuildingsDSM, FabDEM, OpenUrban, AlbedoCloudMasked
from tests.resources.bbox_constants import GEOEXTENT_TERESINA, GEOEXTENT_FLORIANOPOLIS
from tests.resources.conftest import DUMP_RUN_LEVEL, DumpRunLevel
from tests.tools.general_tools import get_test_cache_variables

TEST_BUCKET = CIF_TESTING_S3_BUCKET_URI

# GEO_EXTENT = GEOEXTENT_FLORIANOPOLIS
GEO_EXTENT = GEOEXTENT_TERESINA

# 8-10 min runtime for Teresina
# 46 mins for Florianopolis
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_fabdem_city():
    layer_obj = FabDEM()
    layer_obj.cache_city_data(bbox=GEO_EXTENT, s3_bucket=TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, force_data_refresh=True, spatial_resolution=1)
    _, file_uri, _, _ = get_test_cache_variables(layer_obj, GEO_EXTENT)
    time.sleep(10)
    tiled_file_uri = file_uri + '/geotiff_index.json'
    cache_file_exists = True if check_if_cache_object_exists(file_uri) or check_if_cache_object_exists(tiled_file_uri) else False
    assert cache_file_exists

# 4 min runtime for Teresina
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_open_urban_city():
    layer_obj = OpenUrban()
    layer_obj.cache_city_data(bbox=GEO_EXTENT, s3_bucket=TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, force_data_refresh=True, spatial_resolution=1)
    _, file_uri, _, _ = get_test_cache_variables(layer_obj, GEO_EXTENT)
    time.sleep(10)
    tiled_file_uri = file_uri + '/geotiff_index.json'
    cache_file_exists = True if check_if_cache_object_exists(file_uri) or check_if_cache_object_exists(tiled_file_uri) else False
    assert cache_file_exists

# 7 min runtime for Teresina
# 26 min Florianopolis
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_tree_canopy_height_city():
    layer_obj = TreeCanopyHeight()
    layer_obj.cache_city_data(bbox=GEO_EXTENT, s3_bucket=TEST_BUCKET,  s3_env=DEFAULT_DEVELOPMENT_ENV, force_data_refresh=True, spatial_resolution=1)
    _, file_uri, _, _ = get_test_cache_variables(layer_obj, GEO_EXTENT)
    time.sleep(10)
    tiled_file_uri = file_uri + '/geotiff_index.json'
    cache_file_exists = True if check_if_cache_object_exists(file_uri) or check_if_cache_object_exists(tiled_file_uri) else False
    assert cache_file_exists

# 10 min runtime for Teresina
# 38-41 min Florianopolis
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_albedo_cloud_mask_city():
    layer_obj = AlbedoCloudMasked()
    layer_obj.cache_city_data(bbox=GEO_EXTENT, s3_bucket=TEST_BUCKET,  s3_env=DEFAULT_DEVELOPMENT_ENV, force_data_refresh=True, spatial_resolution=1)
    _, file_uri, _, _ = get_test_cache_variables(layer_obj, GEO_EXTENT)
    time.sleep(10)
    tiled_file_uri = file_uri + '/geotiff_index.json'
    cache_file_exists = True if check_if_cache_object_exists(file_uri) or check_if_cache_object_exists(tiled_file_uri) else False
    assert cache_file_exists

# 52 min runtime for Teresina
# 131 min Florianopolis
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_overture_buildings_dsm_city():
    layer_obj = OvertureBuildingsDSM()
    layer_obj.cache_city_data(bbox=GEO_EXTENT, s3_bucket=TEST_BUCKET,  s3_env=DEFAULT_DEVELOPMENT_ENV, force_data_refresh=True, spatial_resolution=1)
    _, file_uri, _, _ = get_test_cache_variables(layer_obj, GEO_EXTENT)
    time.sleep(10)
    tiled_file_uri = file_uri + '/geotiff_index.json'
    cache_file_exists = True if check_if_cache_object_exists(file_uri) or check_if_cache_object_exists(tiled_file_uri) else False
    assert cache_file_exists
