# This code is mostly intended for manual execution
# Execution configuration is specified in the conftest file
import pytest

from city_metrix.layers import *
from .conftest import RUN_DUMPS, prep_output_path, verify_file_is_populated, get_file_count_in_folder
from ...tools.general_tools import get_class_default_spatial_resolution


@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_albedo_tiled_unbuffered(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, 'albedo_tiled.tif')
    target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(Albedo())
    (Albedo(spatial_resolution=target_resolution).
     write(bbox_info.bounds, file_path, tile_degrees=0.01, buffer_size=None))
    file_count = get_file_count_in_folder(file_path)

    expected_file_count = 5 # includes 4 tiles and one geojson file
    assert file_count == expected_file_count

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_albedo_tiled_buffered(target_folder, bbox_info, target_spatial_resolution_multiplier):
    buffer_degrees = 0.001
    file_path = prep_output_path(target_folder, 'albedo_tiled_buffered.tif')
    target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(Albedo())
    (Albedo(spatial_resolution=target_resolution).
     write(bbox_info.bounds, file_path, tile_degrees=0.01, buffer_size=buffer_degrees))
    file_count = get_file_count_in_folder(file_path)

    expected_file_count = 6 # includes 4 tiles and two geojson files
    assert file_count == expected_file_count