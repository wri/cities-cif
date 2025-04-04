# This code is mostly intended for manual execution
# Execution configuration is specified in the conftest file
import os

import pytest
import geopandas as gpd
import pandas as pd

from city_metrix.constants import WGS_CRS
from city_metrix.metrics import *
from tests.conftest import create_fishnet_grid_for_testing
from tests.resources.bbox_constants import BBOX_IDN_JAKARTA, BBOX_USA_OR_PORTLAND, BBOX_USA_OR_PORTLAND_1, \
    BBOX_USA_OR_PORTLAND_2
from tests.resources.conftest import prep_output_path, verify_file_is_populated
from tests.tools.general_tools import create_target_folder

# SAMPLE_TILED_ZONES = (
#     create_fishnet_grid_for_testing(BBOX_IDN_JAKARTA.coords, 0.01).reset_index())

SAMPLE_TILED_ZONES = (
    create_fishnet_grid_for_testing(BBOX_USA_OR_PORTLAND_2.coords, 0.005).reset_index())


from shapely.geometry import Polygon
polygon_coords = \
    [(-48.823576236608503, -27.431457531700953), (-48.666386558842795, -27.314448678159017),
     (-48.476834300360629, -27.373994958643205), (-48.467587848727355, -27.58112998150985),
     (-48.622465913584726, -27.68352771155466), (-48.735734946092371, -27.640532334533216),
     (-48.823576236608503, -27.431457531700953)]
BRA_Florianopolis_zone = gpd.GeoDataFrame([Polygon(polygon_coords)], columns=["geometry"]).set_crs(WGS_CRS).reset_index()


# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_built_land_with_high_land_surface_temperature(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'built_land_with_high_land_surface_temperature.geojson')

    BuiltLandWithHighLandSurfaceTemperatureMetric().write(zones, file_path)
    assert verify_file_is_populated(file_path)

# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_built_land_with_low_surface_reflectivity(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'built_land_with_low_surface_reflectivity.geojson')

    BuiltLandWithLowSurfaceReflectivity().write(zones, file_path)
    assert verify_file_is_populated(file_path)

# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_built_land_without_tree_cover(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'built_land_without_tree_cover.geojson')

    BuiltLandWithoutTreeCover().write(zones, file_path)
    assert verify_file_is_populated(file_path)


# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_canopy_area_per_resident(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'canopy_area_per_resident.geojson')

    CanopyAreaPerResident().write(zones, file_path)
    assert verify_file_is_populated(file_path)


# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_canopy_area_per_resident_children(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'canopy_area_per_resident_children.geojson')

    CanopyAreaPerResidentChildren().write(zones, file_path)
    assert verify_file_is_populated(file_path)

# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_canopy_area_per_resident_elderly(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'canopy_area_per_resident_elderly.geojson')

    CanopyAreaPerResidentElderly().write(zones, file_path)
    assert verify_file_is_populated(file_path)

# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_canopy_area_per_resident_female(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'canopy_area_per_resident_female.geojson')

    CanopyAreaPerResidentFemale().write(zones, file_path)
    assert verify_file_is_populated(file_path)

# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_canopy_area_per_resident_informal(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'canopy_area_per_resident_informal.geojson')

    CanopyAreaPerResidentInformal().write(zones, file_path)
    assert verify_file_is_populated(file_path)

# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
# TODO - results in geoseries as a list. Why?
# TODO add variants
def test_write_mean_pm2p5_exposure(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'mean_pm2p5_exposure.geojson')

    MeanPM2P5Exposure().write(zones, file_path)
    assert verify_file_is_populated(file_path)

# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_mean_tree_cover(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'mean_tree_cover.geojson')

    indicator = mean_tree_cover(zones)
    gdf = pd.concat([zones, indicator], axis=1)
    gdf.to_file(file_path, driver="GeoJSON")
    assert verify_file_is_populated(file_path)


# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_natural_areas(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'natural_areas.geojson')

    NaturalAreasMetric().write(zones, file_path)
    assert verify_file_is_populated(file_path)

# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_percent_area_impervious(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'percent_area_impervious.geojson')

    indicator = percent_area_impervious(zones)
    gdf = pd.concat([zones, indicator], axis=1)
    gdf.to_file(file_path, driver="GeoJSON")
    assert verify_file_is_populated(file_path)


# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_percent_protected_area(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'percent_protected_area.geojson')

    indicator = percent_protected_area(zones)
    gdf = pd.concat([zones, indicator], axis=1)
    gdf.to_file(file_path, driver="GeoJSON")
    assert verify_file_is_populated(file_path)


# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_recreational_space_per_capita(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'recreational_space_per_capita.geojson')

    indicator = recreational_space_per_capita(zones)
    indicator.name = 'indicator'
    gdf = pd.concat([zones, indicator], axis=1)
    gdf.to_file(file_path, driver="GeoJSON")
    assert verify_file_is_populated(file_path)


# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_urban_open_space(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'urban_open_space.geojson')

    indicator = urban_open_space(zones)
    gdf = pd.concat([zones, indicator], axis=1)
    gdf.to_file(file_path, driver="GeoJSON")
    assert verify_file_is_populated(file_path)


# @pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_vegetation_water_change_gain_area(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'vegetation_water_change_gain_area.geojson')

    indicator = vegetation_water_change_gain_area(zones)
    gdf = pd.concat([zones, indicator], axis=1)
    gdf.to_file(file_path, driver="GeoJSON")
    assert verify_file_is_populated(file_path)




# ==============================================


def test_write_natural_areas_polygon(target_folder):
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'BRA_Florianopolis_natural_areas_polygon.geojson')

    NaturalAreasMetric().write(BRA_Florianopolis_zone, file_path)
    assert verify_file_is_populated(file_path)

