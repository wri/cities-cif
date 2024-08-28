from city_metrix.layers import (
    Albedo,
    AlosDSM,
    AverageNetBuildingHeight,
    EsaWorldCover,
    EsaWorldCoverClass,
    LandSurfaceTemperature,
    NasaDEM,
    NaturalAreas,
    TreeCanopyHeight,
    TreeCover,
    UrbanLandUse,
    WorldPop, NdviSentinel2, BuiltUpHeight
)
from tests.resources.bbox_constants import BBOX_BRA_LAURO_DE_FREITAS_1

COUNTRY_CODE_FOR_BBOX = 'BRA'
BBOX = BBOX_BRA_LAURO_DE_FREITAS_1

def test_albedo_scale():
    doubled_default_resolution = 2 * Albedo().scale_meters
    layer = Albedo(scale_meters=doubled_default_resolution)
    evaluate_layer(layer, doubled_default_resolution)

def test_alos_dsm_scale():
    doubled_default_resolution = 2 * AlosDSM().scale_meters
    layer = AlosDSM(scale_meters=doubled_default_resolution)
    evaluate_layer(layer, doubled_default_resolution)

def test_average_net_building_height_scale():
    doubled_default_resolution = 2 * AverageNetBuildingHeight().scale_meters
    layer = AverageNetBuildingHeight(scale_meters=doubled_default_resolution)
    evaluate_layer(layer, doubled_default_resolution)

def test_built_up_height_scale():
    doubled_default_resolution = 2 * BuiltUpHeight().scale_meters
    layer = BuiltUpHeight(scale_meters=doubled_default_resolution)
    evaluate_layer(layer, doubled_default_resolution)

def test_esa_world_cover_scale():
    doubled_default_resolution = 2 * EsaWorldCover().scale_meters
    layer = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP, scale_meters=doubled_default_resolution)
    evaluate_layer(layer, doubled_default_resolution)

#  TODO
# def test_high_land_surface_temperature_scale():

def test_land_surface_temperature_scale():
    doubled_default_resolution = 2 * LandSurfaceTemperature().scale_meters
    layer = LandSurfaceTemperature(scale_meters=doubled_default_resolution)
    evaluate_layer(layer, doubled_default_resolution)

def test_nasa_dem_scale():
    doubled_default_resolution = 2 * NasaDEM().scale_meters
    layer = NasaDEM(scale_meters=doubled_default_resolution)
    evaluate_layer(layer, doubled_default_resolution)

def test_natural_areas_scale():
    doubled_default_resolution = 2 * NaturalAreas().scale_meters
    layer = NaturalAreas(scale_meters=doubled_default_resolution)
    evaluate_layer(layer, doubled_default_resolution)

def test_ndvi_sentinel2_scale():
    doubled_default_resolution = 2 * NdviSentinel2().scale_meters
    layer = NdviSentinel2(year=2023, scale_meters=doubled_default_resolution)
    evaluate_layer(layer, doubled_default_resolution)

# TODO
# def test_smart_surface_lulc_scale():

def test_tree_canopy_height():
    doubled_default_resolution = 2 * TreeCanopyHeight().scale_meters
    layer = TreeCanopyHeight(scale_meters=doubled_default_resolution)
    evaluate_layer(layer, doubled_default_resolution)

def test_tree_cover():
    doubled_default_resolution = 2 * TreeCover().scale_meters
    layer = TreeCover(scale_meters=doubled_default_resolution)
    evaluate_layer(layer, doubled_default_resolution)

def test_urban_land_use():
    doubled_default_resolution = 2 * UrbanLandUse().scale_meters
    layer = UrbanLandUse(scale_meters=doubled_default_resolution)
    evaluate_layer(layer, doubled_default_resolution)

def test_world_pop():
    doubled_default_resolution = 2 * WorldPop().scale_meters
    layer = WorldPop(scale_meters=doubled_default_resolution)
    evaluate_layer(layer, doubled_default_resolution)


def evaluate_layer(layer, expected_resolution):
    data = layer.get_data(BBOX)
    est_actual_resolution = get_resolution_estimate(data)
    assert expected_resolution == est_actual_resolution

def get_resolution_estimate(data):
    y_cells = data['y'].size - 1
    y_min = data['y'].values.min()
    y_max = data['y'].values.max()
    y_diff = y_max - y_min
    ry = round(y_diff/y_cells)
    return ry
