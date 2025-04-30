import pytest

from city_metrix.layers import *
from tests.resources.bbox_constants import BBOX_USA_OR_PORTLAND_2
from tests.resources.conftest import DUMP_RUN_LEVEL, DumpRunLevel
from tests.resources.tools import get_test_bbox, prep_output_path, verify_file_is_populated

# These tests use a small bbox so that processing completes in a reasonably-short time interval.
CITY_UT_NAME = 'vancouver'
BBOX = BBOX_USA_OR_PORTLAND_2

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_FractionalVegetation_write_small_bbox(target_folder):
    file_path = prep_output_path(target_folder, 'layer','FractionalVegetation_small_bbox.geojson')
    bbox = get_test_bbox(BBOX)
    FractionalVegetation().write(bbox, file_path, tile_side_length=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_UtGlobus_write_small_bbox(target_folder):
    file_path = prep_output_path(target_folder, 'layer','UTGlobus_small_bbox.geojson')
    bbox = get_test_bbox(BBOX)
    UtGlobus(CITY_UT_NAME).write(bbox, file_path, tile_side_length=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_OvertureBuildingsHeight_write_small_bbox(target_folder):
    file_path = prep_output_path(target_folder, 'layer','OvertureBuildingsHeight_small_bbox.geojson')
    bbox = get_test_bbox(BBOX)
    OvertureBuildingsHeight(CITY_UT_NAME).write(bbox, file_path, tile_side_length=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_OvertureBuildingsDSM_write_small_bbox(target_folder):
    file_path = prep_output_path(target_folder, 'layer','OvertureBuildingsDSM_small_bbox.tif')
    bbox = get_test_bbox(BBOX)
    OvertureBuildingsDSM().write(bbox, file_path, tile_side_length=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_SmartSurfaceLULC_write_small_bbox(target_folder):
    file_path = prep_output_path(target_folder, 'layer','SmartSurfaceLULC_small_bbox.tif')
    bbox = get_test_bbox(BBOX)
    SmartSurfaceLULC().write(bbox, file_path, tile_side_length=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_TreeCanopyHeight_write_small_bbox(target_folder):
    file_path = prep_output_path(target_folder, 'layer','TreeCanopyHeight_small_bbox.tif')
    bbox = get_test_bbox(BBOX)
    TreeCanopyHeight().write(bbox, file_path, tile_side_length=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_TreeCanopyCoverMask_write_small_bbox(target_folder):
    file_path = prep_output_path(target_folder, 'layer','TreeCanopyHeight_small_bbox.tif')
    bbox = get_test_bbox(BBOX)
    TreeCanopyCoverMask().write(bbox, file_path, tile_side_length=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_UtGlobus_write_small_bbox(target_folder):
    file_path = prep_output_path(target_folder, 'layer','UtGlobus_small_bbox.geojson')
    bbox = get_test_bbox(BBOX)
    UtGlobus(CITY_UT_NAME).write(bbox, file_path, tile_side_length=None)
    assert verify_file_is_populated(file_path)

