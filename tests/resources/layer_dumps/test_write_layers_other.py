# This code is mostly intended for manual execution
# Execution configuration is specified in the conftest file
import pytest
import xarray as xr

from city_metrix.layers import *
from tests.resources.conftest import DUMP_RUN_LEVEL, prep_output_path, get_file_count_in_folder, DumpRunLevel
from tests.resources.tools import get_test_bbox, get_test_resolution


@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_albedo_tiled_unbuffered(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'albedo_tiled.tif')
    target_resolution = get_test_resolution(Albedo())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    (Albedo()
     .write(bbox, file_path, tile_side_length=0.01, buffer_size=None, length_units="degrees",
            spatial_resolution=target_resolution))
    file_count = get_file_count_in_folder(file_path)

    expected_file_count = 3 # includes 2 tiles and one json file
    assert file_count == expected_file_count

@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_albedo_tiled_buffered(target_folder, sample_aoi):
    buffer_degrees = 0.001
    file_path = prep_output_path(target_folder, 'albedo_tiled_buffered.tif')
    target_resolution = get_test_resolution(Albedo())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    (Albedo()
     .write(bbox, file_path, tile_side_length=0.01, buffer_size=buffer_degrees, length_units="degrees",
            spatial_resolution=target_resolution))
    file_count = get_file_count_in_folder(file_path)

    expected_file_count = 4 # includes 2 tiles and two json files
    assert file_count == expected_file_count


@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_nasa_dem_tiled_unbuffered(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'nasa_dem_tiled_unbuffered.tif')
    target_resolution = get_test_resolution(NasaDEM())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    (NasaDEM()
     .write(bbox, file_path,
            tile_side_length=.008, length_units='degrees',
            spatial_resolution=target_resolution, resampling_method='bilinear'))

    file_count = get_file_count_in_folder(file_path)
    expected_file_count = 5 # includes 4 tiles and 1 json files
    assert file_count == expected_file_count


@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_get_nasa_dem_bicubic(target_folder, sample_aoi):
    utm_bbox = get_test_bbox(sample_aoi.geo_extent).as_utm_bbox()
    data = NasaDEM().get_data(utm_bbox, spatial_resolution=30, resampling_method='bicubic')

    assert isinstance(data, xr.DataArray)
    assert data.crs == utm_bbox.crs
