# This code is mostly intended for manual execution
# Execution configuration is specified in the conftest file
import pytest

from city_metrix.layers import *
from .conftest import RUN_DUMPS, prep_output_path, verify_file_is_populated

TARGET_RESOLUTION = 5
TARGET_RESAMPLING_METHOD = 'bilinear'

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_albedo_fixed_res(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, f'albedo_{TARGET_RESOLUTION}m.tif')
    (Albedo(spatial_resolution=TARGET_RESOLUTION, resampling_method=TARGET_RESAMPLING_METHOD)
     .write(bbox_info.bounds, file_path, tile_degrees=None))
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_alos_dsm_fixed_res(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, f'alos_dsm_{TARGET_RESOLUTION}m.tif')
    (AlosDSM(spatial_resolution=TARGET_RESOLUTION, resampling_method=TARGET_RESAMPLING_METHOD)
     .write(bbox_info.bounds, file_path, tile_degrees=None))
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_average_net_building_height_fixed_res(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, f'average_net_building_height_{TARGET_RESOLUTION}m.tif')
    AverageNetBuildingHeight(spatial_resolution=TARGET_RESOLUTION).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_built_up_height_fixed_res(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, f'built_up_height_{TARGET_RESOLUTION}m.tif')
    BuiltUpHeight(spatial_resolution=TARGET_RESOLUTION).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_esa_world_cover_fixed_res(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, f'esa_world_cover_{TARGET_RESOLUTION}m.tif')
    EsaWorldCover(spatial_resolution=TARGET_RESOLUTION).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_glad_lulc_fixed_res(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, f'glad_lulc_{TARGET_RESOLUTION}m.tif')
    LandCoverGlad(spatial_resolution=TARGET_RESOLUTION).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_high_land_surface_temperature_fixed_res(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, f'high_land_surface_temperature_{TARGET_RESOLUTION}m.tif')
    HighLandSurfaceTemperature(spatial_resolution=TARGET_RESOLUTION).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_impervious_surface_fixed_res(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, f'impervious_surface_{TARGET_RESOLUTION}m.tif')
    ImperviousSurface(spatial_resolution=TARGET_RESOLUTION).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_land_surface_temperature_fixed_res(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, f'land_surface_temperature_{TARGET_RESOLUTION}m.tif')
    LandSurfaceTemperature(spatial_resolution=TARGET_RESOLUTION).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_nasa_dem_fixed_res(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, f'nasa_dem_{TARGET_RESOLUTION}m.tif')
    (NasaDEM(spatial_resolution=TARGET_RESOLUTION, resampling_method=TARGET_RESAMPLING_METHOD)
     .write(bbox_info.bounds, file_path, tile_degrees=None))
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_natural_areas_fixed_res(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, f'natural_areas_{TARGET_RESOLUTION}m.tif')
    NaturalAreas(spatial_resolution=TARGET_RESOLUTION).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_ndvi_sentinel2_gee_fixed_res(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, f'ndvi_sentinel2_gee_{TARGET_RESOLUTION}m.tif')
    NdviSentinel2(year=2023, spatial_resolution=TARGET_RESOLUTION).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_smart_surface_lulc_fixed_res(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, f'smart_surface_lulc_{TARGET_RESOLUTION}m.tif')
    SmartSurfaceLULC(spatial_resolution=TARGET_RESOLUTION).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_tree_canopy_height_fixed_res(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, f'tree_canopy_height_{TARGET_RESOLUTION}m.tif')
    TreeCanopyHeight(spatial_resolution=TARGET_RESOLUTION).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_tree_cover_fixed_res(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, f'tree_cover_{TARGET_RESOLUTION}m.tif')
    TreeCover(spatial_resolution=TARGET_RESOLUTION).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_urban_land_use_fixed_res(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, f'urban_land_use_{TARGET_RESOLUTION}m.tif')
    UrbanLandUse(spatial_resolution=TARGET_RESOLUTION).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_world_pop_fixed_res(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, f'world_pop_{TARGET_RESOLUTION}m.tif')
    WorldPop(spatial_resolution=TARGET_RESOLUTION).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

