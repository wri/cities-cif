# This code is mostly intended for manual execution
# Execution configuration is specified in the conftest file
import pytest

from city_metrix.layers import (
    Albedo,
    AlosDSM,
    AverageNetBuildingHeight,
    EsaWorldCover,
    HighLandSurfaceTemperature,
    LandsatCollection2,
    LandSurfaceTemperature,
    NasaDEM,
    NaturalAreas,
    OpenBuildings,
    OpenStreetMap,
    OvertureBuildings,
    Sentinel2Level2,
    NdviSentinel2,
    SmartSurfaceLULC,
    TreeCanopyHeight,
    TreeCover,
    UrbanLandUse,
    WorldPop, Layer
)
from .conftest import RUN_DUMPS, prep_output_path, verify_file_is_populated
from ...tools.general_tools import get_class_default_spatial_resolution


@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_albedo(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, 'albedo.tif')
    target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(Albedo())
    Albedo(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_alos_dsm(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, 'alos_dsm.tif')
    target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(AlosDSM())
    AlosDSM(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_average_net_building_height(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, 'average_net_building_height.tif')
    target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(AverageNetBuildingHeight())
    AverageNetBuildingHeight(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_esa_world_cover(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, 'esa_world_cover.tif')
    target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(EsaWorldCover())
    EsaWorldCover(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_high_land_surface_temperature(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, 'high_land_surface_temperature.tif')
    target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(HighLandSurfaceTemperature())
    HighLandSurfaceTemperature(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_land_surface_temperature(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, 'land_surface_temperature.tif')
    target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(LandSurfaceTemperature())
    LandSurfaceTemperature(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

# TODO Class is no longer used, but may be useful later
# @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
# def test_write_landsat_collection_2(target_folder, bbox_info, target_spatial_resolution_multiplier):
#     file_path = prep_output_path(target_folder, 'landsat_collection2.tif')
#     bands = ['green']
#     LandsatCollection2(bands).write(bbox_info.bounds, file_path, tile_degrees=None)
#     assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_nasa_dem(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, 'nasa_dem.tif')
    target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(NasaDEM())
    NasaDEM(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_natural_areas(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, 'natural_areas.tif')
    target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(NaturalAreas())
    NaturalAreas(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_ndvi_sentinel2_gee(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, 'ndvi_sentinel2_gee.tif')
    target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(NdviSentinel2())
    NdviSentinel2(year=2023, spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_openbuildings(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, 'open_buildings.tif')
    OpenBuildings(bbox_info.country).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

# TODO Class write is not functional. Is class still needed or have we switched to overture?
# @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
# def test_write_open_street_map(target_folder, bbox_info, target_spatial_resolution_multiplier):
#     file_path = prep_output_path(target_folder, 'open_street_map.tif')
#     OpenStreetMap().write(bbox_info.bounds, file_path, tile_degrees=None)
#     assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_overture_buildings(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, 'overture_buildings.tif')
    OvertureBuildings().write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

# TODO Class is no longer used, but may be useful later
# @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
# def test_write_sentinel_2_level2(target_folder, bbox_info, target_spatial_resolution_multiplier):
#     file_path = prep_output_path(target_folder, 'sentinel_2_level2.tif')
#     sentinel_2_bands = ["green"]
#     Sentinel2Level2(sentinel_2_bands).write(bbox_info.bounds, file_path, tile_degrees=None)
#     assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_smart_surface_lulc(target_folder, bbox_info, target_spatial_resolution_multiplier):
    # Note: spatial_resolution not implemented for this raster class
    file_path = prep_output_path(target_folder, 'smart_surface_lulc.tif')
    SmartSurfaceLULC().write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_tree_canopy_height(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, 'tree_canopy_height.tif')
    target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(TreeCanopyHeight())
    TreeCanopyHeight(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_tree_cover(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, 'tree_cover.tif')
    target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(TreeCover())
    TreeCover(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_urban_land_use(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, 'urban_land_use.tif')
    target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(UrbanLandUse())
    UrbanLandUse(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_write_world_pop(target_folder, bbox_info, target_spatial_resolution_multiplier):
    file_path = prep_output_path(target_folder, 'world_pop.tif')
    target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(WorldPop())
    WorldPop(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)
