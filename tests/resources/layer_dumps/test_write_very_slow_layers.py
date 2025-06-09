import pytest

from city_metrix.constants import DEFAULT_DEVELOPMENT_ENV, DEFAULT_STAGING_ENV
from city_metrix.layers import *
from tests.resources.bbox_constants import BBOX_USA_OR_PORTLAND_2
from tests.resources.conftest import DUMP_RUN_LEVEL, DumpRunLevel
from tests.resources.tools import get_test_bbox, prep_output_path, verify_file_is_populated, cleanup_cache_files

# These tests use a small bbox so that processing completes in a reasonably-short time interval.
CITY_UT_NAME = 'vancouver'
BBOX = BBOX_USA_OR_PORTLAND_2

# @pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
# def test_FractionalVegetation_write_small_bbox(target_folder):
#     file_path = prep_output_path(target_folder, 'layer','FractionalVegetation_small_bbox.tif')
#     bbox = get_test_bbox(BBOX)
#     layer_obj = FractionalVegetation()
#     _write_verify(layer_obj, bbox, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_OvertureBuildingsHeight_write_small_bbox(target_folder):
    file_path = prep_output_path(target_folder, 'layer','OvertureBuildingsHeight_small_bbox.geojson')
    bbox = get_test_bbox(BBOX)
    layer_obj = OvertureBuildingsHeight(CITY_UT_NAME)
    _write_verify(layer_obj, bbox, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_OvertureBuildingsDSM_write_small_bbox(target_folder):
    file_path = prep_output_path(target_folder, 'layer','OvertureBuildingsDSM_small_bbox.tif')
    bbox = get_test_bbox(BBOX)
    layer_obj = OvertureBuildingsDSM()
    _write_verify(layer_obj, bbox, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_open_urban_write_small_bbox(target_folder):
    file_path = prep_output_path(target_folder, 'layer','OpenUrban_small_bbox.tif')
    bbox = get_test_bbox(BBOX)
    layer_obj = OpenUrban()
    _write_verify(layer_obj, bbox, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_SmartSurfaceLULC_write_small_bbox(target_folder):
    file_path = prep_output_path(target_folder, 'layer','SmartSurfaceLULC_small_bbox.tif')
    bbox = get_test_bbox(BBOX)
    layer_obj = SmartSurfaceLULC()
    _write_verify(layer_obj, bbox, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_TreeCanopyHeight_write_small_bbox(target_folder):
    file_path = prep_output_path(target_folder, 'layer','TreeCanopyHeight_small_bbox.tif')
    bbox = get_test_bbox(BBOX)
    layer_obj = TreeCanopyHeight()
    _write_verify(layer_obj, bbox, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_TreeCanopyCoverMask_write_small_bbox(target_folder):
    file_path = prep_output_path(target_folder, 'layer','TreeCanopyHeight_small_bbox.tif')
    bbox = get_test_bbox(BBOX)
    layer_obj = TreeCanopyCoverMask()
    _write_verify(layer_obj, bbox, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_UtGlobus_write_small_bbox(target_folder):
    file_path = prep_output_path(target_folder, 'layer','UtGlobus_small_bbox.geojson')
    bbox = get_test_bbox(BBOX)
    layer_obj = UtGlobus(CITY_UT_NAME)
    _write_verify(layer_obj, bbox, file_path)

def _write_verify(layer_obj, bbox, file_path):
    layer_obj.write(bbox=bbox, s3_env=DEFAULT_DEVELOPMENT_ENV, output_uri=file_path, tile_side_length=None)
    assert verify_file_is_populated(file_path)
    cleanup_cache_files(None, None, None, file_path)