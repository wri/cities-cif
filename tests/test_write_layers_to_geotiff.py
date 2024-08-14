import pytest
import os
import shutil

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
    SmartSurfaceLULC,
    TreeCanopyHeight,
    TreeCover,
    UrbanLandUse,
    WorldPop
)
from tests.fixtures.bbox_constants import *
from tools.general_tools import create_temp_folder, verify_file_is_populated

RUN_DUMPS = False
BBOX = BBOX_BR_LAURO_DE_FREITAS_1

@pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
def test_prepare_target():
    qgis_project_file = 'layers_for_br_lauro_de_freitas.qgs'

    source_folder = os.path.join(os.path.dirname(__file__), 'resources')
    output_temp_folder = create_temp_folder('test_result_tif_files')
    source_qgis_file = os.path.join(source_folder, qgis_project_file)
    target_qgis_file = os.path.join(output_temp_folder, qgis_project_file)
    shutil.copyfile(source_qgis_file, target_qgis_file)

    process_layers(output_temp_folder)


def process_layers(output_temp_folder):
    write_albedo(output_temp_folder)
    write_alos_dsm(output_temp_folder)
    write_average_net_building_height(output_temp_folder)
    write_esa_world_cover(output_temp_folder)
    write_high_land_surface_temperature(output_temp_folder)
    write_land_surface_temperature(output_temp_folder)
    # write_landsat_collection_2(output_temp_folder)
    write_nasa_dem(output_temp_folder)
    write_natural_areas(output_temp_folder)
    write_openbuildings(output_temp_folder)
    # write_open_street_map(output_temp_folder)
    write_overture_buildings(output_temp_folder)
    # write_sentinel_2_level2(output_temp_folder)
    write_smart_surface_lulc(output_temp_folder)
    write_tree_canopy_height(output_temp_folder)
    write_tree_cover(output_temp_folder)
    write_urban_land_use(output_temp_folder)
    write_world_pop(output_temp_folder)


def write_albedo(output_temp_folder):
    file_path = prep_output_path(output_temp_folder, 'albedo.tif')
    Albedo().write(BBOX, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

def write_alos_dsm(output_temp_folder):
    file_path = prep_output_path(output_temp_folder, 'alos_dsm.tif')
    AlosDSM().write(BBOX, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

def write_average_net_building_height(output_temp_folder):
    file_path = prep_output_path(output_temp_folder, 'average_net_building_height.tif')
    AverageNetBuildingHeight().write(BBOX, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

def write_esa_world_cover(output_temp_folder):
    file_path = prep_output_path(output_temp_folder, 'esa_world_cover.tif')
    EsaWorldCover().write(BBOX, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

def write_high_land_surface_temperature(output_temp_folder):
    file_path = prep_output_path(output_temp_folder, 'high_land_surface_temperature.tif')
    HighLandSurfaceTemperature().write(BBOX, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

def write_land_surface_temperature(output_temp_folder):
    file_path = prep_output_path(output_temp_folder, 'land_surface_temperature.tif')
    LandSurfaceTemperature().write(BBOX, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

# TODO: Determine how to output xarray.Dataset with time dimension for QGIS rendering
# def write_landsat_collection_2(output_temp_folder):
#     file_path = prep_output_path(output_temp_folder, 'landsat_collection2.tif')
#     bands = ['green']
#     LandsatCollection2(bands).write(BBOX, file_path, tile_degrees=None)
#     assert verify_file_is_populated(file_path)

def write_nasa_dem(output_temp_folder):
    file_path = prep_output_path(output_temp_folder, 'nasa_dem.tif')
    NasaDEM().write(BBOX, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

def write_natural_areas(output_temp_folder):
    file_path = prep_output_path(output_temp_folder, 'natural_areas.tif')
    NaturalAreas().write(BBOX, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

def write_openbuildings(output_temp_folder):
    file_path = prep_output_path(output_temp_folder, 'open_buildings.tif')
    OpenBuildings().write(BBOX, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

# TODO: class function "write" does not properly handle call
# def write_open_street_map(output_temp_folder):
#     file_path = prep_output_path(output_temp_folder, 'open_street_map.tif')
#     OpenStreetMap().write(BBOX, file_path, tile_degrees=None)
#     assert verify_file_is_populated(file_path)

def write_overture_buildings(output_temp_folder):
    file_path = prep_output_path(output_temp_folder, 'overture_buildings.tif')
    OvertureBuildings().write(BBOX, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

# TODO: Determine how to output xarray.Dataset with time dimension for QGIS rendering
# def write_sentinel_2_level2(output_temp_folder):
#     file_path = prep_output_path(output_temp_folder, 'sentinel_2_level2.tif')
#     sentinel_2_bands = ["green"]
#     Sentinel2Level2(sentinel_2_bands).write(BBOX, file_path, tile_degrees=None)
#     assert verify_file_is_populated(file_path)

def write_smart_surface_lulc(output_temp_folder):
    file_path = prep_output_path(output_temp_folder, 'smart_surface_lulc.tif')
    SmartSurfaceLULC().write(BBOX, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

def write_tree_canopy_height(output_temp_folder):
    file_path = prep_output_path(output_temp_folder, 'tree_canopy_height.tif')
    TreeCanopyHeight().write(BBOX, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

def write_tree_cover(output_temp_folder):
    file_path = prep_output_path(output_temp_folder, 'tree_cover.tif')
    TreeCover().write(BBOX, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

def write_urban_land_use(output_temp_folder):
    file_path = prep_output_path(output_temp_folder, 'urban_land_use.tif')
    UrbanLandUse().write(BBOX, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)

def write_world_pop(output_temp_folder):
    file_path = prep_output_path(output_temp_folder, 'world_pop.tif')
    WorldPop().write(BBOX, file_path, tile_degrees=None)
    assert verify_file_is_populated(file_path)


def prep_output_path(output_temp_folder, file_name):
    file_path = os.path.join(output_temp_folder, file_name)
    if os.path.isfile(file_path):
        os.remove(file_path)
    return file_path
