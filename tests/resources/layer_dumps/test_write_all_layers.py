# This code is mostly intended for manual execution
# Execution configuration is specified in the conftest file
import pytest

from city_metrix.layers import *
from .conftest import EXECUTE_IGNORED_TESTS, prep_output_path, verify_file_is_populated
from .tools import get_test_resolution, get_test_bbox


@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_albedo(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'albedo.tif')
    target_resolution = get_test_resolution(Albedo())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    Albedo().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_alos_dsm(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'alos_dsm.tif')
    target_resolution = get_test_resolution(AlosDSM())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    AlosDSM().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_average_net_building_height(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'average_net_building_height.tif')
    target_resolution = get_test_resolution(AverageNetBuildingHeight())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    AverageNetBuildingHeight().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_built_up_height(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'built_up_height.tif')
    target_resolution = get_test_resolution(BuiltUpHeight())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    BuiltUpHeight().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_cams(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'cams.tx')
    bbox = get_test_bbox(sample_aoi.geo_extent)
    Cams().write(bbox, file_path, tile_side_length=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_era_5_hottest_day(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'era_5_hottest_day.txt')
    bbox = get_test_bbox(sample_aoi.geo_extent)
    Era5HottestDay().write(bbox, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_esa_world_cover(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'esa_world_cover.tif')
    target_resolution = get_test_resolution(EsaWorldCover())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    EsaWorldCover().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_height_above_nearest_drainage(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'height_above_nearest_drainage.tif')
    target_resolution = get_test_resolution(HeightAboveNearestDrainage())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    HeightAboveNearestDrainage().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_high_land_surface_temperature(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'high_land_surface_temperature.tif')
    target_resolution = get_test_resolution(HighLandSurfaceTemperature())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    HighLandSurfaceTemperature().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_high_slope(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'high_slope.tif')
    target_resolution = get_test_resolution(HighSlope())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    HighSlope().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_impervious_surface(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'impervious_surface.tif')
    target_resolution = get_test_resolution(ImperviousSurface())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    ImperviousSurface().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_land_cover_glad(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'glad_lulc.tif')
    target_resolution = get_test_resolution(LandCoverGlad())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    LandCoverGlad().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_land_surface_temperature(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'land_surface_temperature.tif')
    target_resolution = get_test_resolution(LandSurfaceTemperature())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    LandSurfaceTemperature().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

# TODO Class is no longer used, but may be useful later
@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_landsat_collection_2(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'landsat_collection2.tif')
    bbox = get_test_bbox(sample_aoi.geo_extent)
    bands = ['green']
    LandsatCollection2(bands).write(bbox, file_path, tile_side_length=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_nasa_dem(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'nasa_dem.tif')
    target_resolution = get_test_resolution(NasaDEM())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    NasaDEM().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_natural_areas(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'natural_areas.tif')
    target_resolution = get_test_resolution(NaturalAreas())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    NaturalAreas().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_ndvi_sentinel2_gee(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'ndvi_sentinel2_gee.tif')
    target_resolution = get_test_resolution(NdviSentinel2())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    NdviSentinel2(year=2023).write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_openbuildings(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'open_buildings.geojson')
    bbox = get_test_bbox(sample_aoi.geo_extent)
    OpenBuildings(sample_aoi.country).write(bbox, file_path, tile_side_length=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_open_street_map_roads(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'open_street_map_roads.geojson')
    bbox = get_test_bbox(sample_aoi.geo_extent)
    road_features = OpenStreetMapClass.ROAD
    OpenStreetMap(road_features).write(bbox, file_path, tile_side_length=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_overture_buildings(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'overture_buildings.geojson')
    bbox = get_test_bbox(sample_aoi.geo_extent)
    OvertureBuildings().write(bbox, file_path, tile_side_length=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_protected_areas(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'protected_areas.geojson')
    bbox = get_test_bbox(sample_aoi.geo_extent)
    ProtectedAreas().write(bbox, file_path, tile_side_length=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_riparian_areas(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'riparian_areas.tif')
    target_resolution = get_test_resolution(RiparianAreas())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    RiparianAreas().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

# TODO Class is no longer used, but may be useful later
@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_sentinel_2_level2(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'sentinel_2_level2.tif')
    sentinel_2_bands = ["green"]
    bbox = get_test_bbox(sample_aoi.geo_extent)
    Sentinel2Level2(sentinel_2_bands).write(bbox, file_path, tile_side_length=None)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_smart_surface_lulc(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'smart_surface_lulc.tif')
    target_resolution = get_test_resolution(SmartSurfaceLULC())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    SmartSurfaceLULC().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_tree_canopy_height(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'tree_canopy_height.tif')
    target_resolution = get_test_resolution(TreeCanopyHeight())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    TreeCanopyHeight().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_tree_cover(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'tree_cover.tif')
    target_resolution = get_test_resolution(TreeCover())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    TreeCover().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_urban_land_use(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'urban_land_use.tif')
    target_resolution = get_test_resolution(UrbanLandUse())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    UrbanLandUse().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_vegetation_water_map(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'vegetation_water_map.tif')
    target_resolution = get_test_resolution(VegetationWaterMap())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    VegetationWaterMap().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_world_pop(target_folder, sample_aoi):
    file_path = prep_output_path(target_folder, 'world_pop.tif')
    target_resolution = get_test_resolution(WorldPop())
    bbox = get_test_bbox(sample_aoi.geo_extent)
    WorldPop().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

