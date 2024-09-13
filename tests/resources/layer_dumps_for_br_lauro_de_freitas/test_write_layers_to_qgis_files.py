# This code is mostly intended for manual execution
# Execution configuration is specified in the conftest file
import pytest
import os

from city_metrix import built_land_with_high_land_surface_temperature, built_land_with_low_surface_reflectivity, \
    built_land_without_tree_cover, natural_areas, mean_tree_cover, urban_open_space
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
    WorldPop, Layer, ImperviousSurface
)
from city_metrix.metrics.built_land_with_vegetation import built_land_with_vegetation
from .conftest import RUN_DUMPS, prep_output_path, verify_file_is_populated
from ...tools.general_tools import get_class_default_spatial_resolution, create_fishnet_grid, write_metric, \
    get_zones_from_bbox_info


class TestLayerWrite:
    @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    def test_write_albedo(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
        file_path = prep_output_path(target_folder, 'albedo.tif')
        target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(Albedo())
        Albedo(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
        assert verify_file_is_populated(file_path)

    @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    def test_write_alos_dsm(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
        file_path = prep_output_path(target_folder, 'alos_dsm.tif')
        target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(AlosDSM())
        AlosDSM(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
        assert verify_file_is_populated(file_path)

    @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    def test_write_average_net_building_height(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
        file_path = prep_output_path(target_folder, 'average_net_building_height.tif')
        target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(AverageNetBuildingHeight())
        AverageNetBuildingHeight(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
        assert verify_file_is_populated(file_path)

    @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    def test_write_esa_world_cover(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
        file_path = prep_output_path(target_folder, 'esa_world_cover.tif')
        target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(EsaWorldCover())
        EsaWorldCover(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
        assert verify_file_is_populated(file_path)

    @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    def test_write_high_land_surface_temperature(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
        file_path = prep_output_path(target_folder, 'high_land_surface_temperature.tif')
        target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(HighLandSurfaceTemperature())
        HighLandSurfaceTemperature(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
        assert verify_file_is_populated(file_path)

    @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    def test_write_impervious_surface(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
        file_path = prep_output_path(target_folder, 'impervious_surface.tif')
        target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(ImperviousSurface())
        LandSurfaceTemperature(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
        assert verify_file_is_populated(file_path)

    @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    def test_write_land_surface_temperature(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
        file_path = prep_output_path(target_folder, 'land_surface_temperature.tif')
        target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(LandSurfaceTemperature())
        LandSurfaceTemperature(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
        assert verify_file_is_populated(file_path)

    # TODO Class is no longer used, but may be useful later
    # @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    # def test_write_landsat_collection_2(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
    #     file_path = prep_output_path(target_folder, 'landsat_collection2.tif')
    #     bands = ['green']
    #     LandsatCollection2(bands).write(bbox_info.bounds, file_path, tile_degrees=None)
    #     assert verify_file_is_populated(file_path)

    @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    def test_write_nasa_dem(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
        file_path = prep_output_path(target_folder, 'nasa_dem.tif')
        target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(NasaDEM())
        NasaDEM(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
        assert verify_file_is_populated(file_path)

    @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    def test_write_natural_areas(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
        file_path = prep_output_path(target_folder, 'natural_areas.tif')
        target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(NaturalAreas())
        NaturalAreas(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
        assert verify_file_is_populated(file_path)

    @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    def test_write_ndvi_sentinel2_gee(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
        file_path = prep_output_path(target_folder, 'ndvi_sentinel2_gee.tif')
        target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(NdviSentinel2())
        NdviSentinel2(year=2023, ndvi_threshold =0.4, spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
        assert verify_file_is_populated(file_path)

    @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    def test_write_openbuildings(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
        file_path = prep_output_path(target_folder, 'open_buildings.geojson')
        OpenBuildings(bbox_info.country).write(bbox_info.bounds, file_path, tile_degrees=None)
        assert verify_file_is_populated(file_path)

    # TODO Class write is not functional. Is class still needed or have we switched to overture?
    # @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    # def test_write_open_street_map(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
    #     file_path = prep_output_path(target_folder, 'open_street_map.tif')
    #     OpenStreetMap().write(bbox_info.bounds, file_path, tile_degrees=None)
    #     assert verify_file_is_populated(file_path)

    @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    def test_write_overture_buildings(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
        file_path = prep_output_path(target_folder, 'overture_buildings.geojson')
        OvertureBuildings().write(bbox_info.bounds, file_path, tile_degrees=None)
        assert verify_file_is_populated(file_path)

    # TODO Class is no longer used, but may be useful later
    # @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    # def test_write_sentinel_2_level2(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
    #     file_path = prep_output_path(target_folder, 'sentinel_2_level2.tif')
    #     sentinel_2_bands = ["green"]
    #     Sentinel2Level2(sentinel_2_bands).write(bbox_info.bounds, file_path, tile_degrees=None)
    #     assert verify_file_is_populated(file_path)

    @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    def test_write_smart_surface_lulc(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
        # Note: spatial_resolution not implemented for this raster class
        file_path = prep_output_path(target_folder, 'smart_surface_lulc.tif')
        SmartSurfaceLULC().write(bbox_info.bounds, file_path, tile_degrees=None)
        assert verify_file_is_populated(file_path)

    @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    def test_write_tree_canopy_height(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
        file_path = prep_output_path(target_folder, 'tree_canopy_height.tif')
        target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(TreeCanopyHeight())
        TreeCanopyHeight(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
        assert verify_file_is_populated(file_path)

    @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    def test_write_tree_cover(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
        file_path = prep_output_path(target_folder, 'tree_cover.tif')
        target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(TreeCover())
        TreeCover(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
        assert verify_file_is_populated(file_path)

    @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    def test_write_urban_land_use(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
        file_path = prep_output_path(target_folder, 'urban_land_use.tif')
        target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(UrbanLandUse())
        UrbanLandUse(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
        assert verify_file_is_populated(file_path)

    @pytest.mark.skipif(RUN_DUMPS == False, reason='Skipping since RUN_DUMPS set to False')
    def test_write_world_pop(self, target_folder, bbox_info, target_spatial_resolution_multiplier):
        file_path = prep_output_path(target_folder, 'world_pop.tif')
        target_resolution = target_spatial_resolution_multiplier * get_class_default_spatial_resolution(WorldPop())
        WorldPop(spatial_resolution=target_resolution).write(bbox_info.bounds, file_path, tile_degrees=None)
        assert verify_file_is_populated(file_path)

class TestMetricWrite:
    CELL_SIZE = 0.0005
    def test_write_built_land_with_high_land_surface_temperature(self, target_folder, bbox_info):
        zones = get_zones_from_bbox_info(bbox_info, self.CELL_SIZE)
        indicator = built_land_with_high_land_surface_temperature(zones)

        file_path = os.path.join(target_folder,'metric_built_land_with_high_land_surface_temperature.geojson')
        write_metric(indicator, zones, 'count', file_path)

        assert verify_file_is_populated(file_path)

    def test_write_built_land_with_low_surface_reflectivity(self, target_folder, bbox_info):
        zones = get_zones_from_bbox_info(bbox_info, self.CELL_SIZE)
        indicator = built_land_with_low_surface_reflectivity(zones)

        file_path = os.path.join(target_folder,'metric_built_land_with_low_surface_reflectivity.geojson')
        write_metric(indicator, zones, 'count', file_path)

        assert verify_file_is_populated(file_path)

    def test_write_built_land_with_vegetation(self, target_folder, bbox_info):
        zones = get_zones_from_bbox_info(bbox_info, self.CELL_SIZE)
        indicator = built_land_with_vegetation(zones)

        file_path = os.path.join(target_folder,'metric_built_land_with_vegetation.geojson')
        write_metric(indicator, zones, 'count', file_path)

        assert verify_file_is_populated(file_path)

    def test_write_built_land_without_tree_cover(self, target_folder, bbox_info):
        zones = get_zones_from_bbox_info(bbox_info, self.CELL_SIZE)
        indicator = built_land_without_tree_cover(zones)

        file_path = os.path.join(target_folder,'metric_built_land_without_tree_cover.geojson')
        write_metric(indicator, zones, 'count', file_path)

        assert verify_file_is_populated(file_path)

    def test_write_mean_tree_cover(self, target_folder, bbox_info):
        zones = get_zones_from_bbox_info(bbox_info, self.CELL_SIZE)
        indicator = mean_tree_cover(zones)

        file_path = os.path.join(target_folder,'metric_mean_tree_cover.geojson')
        write_metric(indicator, zones, 'mean', file_path)

        assert verify_file_is_populated(file_path)

    def test_write_natural_areas(self, target_folder, bbox_info):
        zones = get_zones_from_bbox_info(bbox_info, self.CELL_SIZE)
        indicator = natural_areas(zones)

        file_path = os.path.join(target_folder,'metric_natural_areas.geojson')
        write_metric(indicator, zones, 'mean', file_path)

        assert verify_file_is_populated(file_path)

    def test_write_urban_open_space(self, target_folder, bbox_info):
        zones = get_zones_from_bbox_info(bbox_info, self.CELL_SIZE)
        indicator = urban_open_space(zones)

        file_path = os.path.join(target_folder,'metric_urban_open_space.geojson')
        write_metric(indicator, zones, 'count', file_path)

        assert verify_file_is_populated(file_path)