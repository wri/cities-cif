from city_metrix import BuiltLandWithLowSurfaceReflectivity
from city_metrix.layers import Albedo, AcagPM2p5, LandCoverHabitatChangeGlad, EsaWorldCover, EsaWorldCoverClass, Cams
from tests.resources.bbox_constants import GEOEXTENT_TERESINA_WGS84
from tests.resources.metrics_dumps.test_write_metric_variants import IDN_Jakarta_zone
from tests.tools.general_tools import get_test_cache_variables


def test_layer_with_year():
    geo_extent = GEOEXTENT_TERESINA_WGS84
    layer_obj = AcagPM2p5()
    file_key, file_uri, layer_id, is_custom_layer = get_test_cache_variables(layer_obj, geo_extent)

    assert layer_id == 'AcagPM2p5__StartYear_2022_EndYear_2022.tif'
    assert is_custom_layer == False

def test_layer_with_start_end_year():
    geo_extent = GEOEXTENT_TERESINA_WGS84
    layer_obj = LandCoverHabitatChangeGlad()
    file_key, file_uri, layer_id, is_custom_layer = get_test_cache_variables(layer_obj, geo_extent)

    assert layer_id == 'LandCoverHabitatChangeGlad__StartYear_2000_EndYear_2020.tif'
    assert is_custom_layer == False

def test_layer_with_start_end_date():
    geo_extent = GEOEXTENT_TERESINA_WGS84
    layer_obj = Albedo()
    file_key, file_uri, layer_id, is_custom_layer = get_test_cache_variables(layer_obj, geo_extent)

    assert layer_id == 'Albedo__StartYear_2021_EndYear_2021.tif'
    assert is_custom_layer == False

def test_layer_with_start_end_date_in_same_year():
    geo_extent = GEOEXTENT_TERESINA_WGS84
    layer_obj = Cams()
    file_key, file_uri, layer_id, is_custom_layer = get_test_cache_variables(layer_obj, geo_extent)

    assert layer_id == 'Cams__StartYear_2023_EndYear_2023.nc'
    assert is_custom_layer == False

def test_layer_with_major_name():
    geo_extent = GEOEXTENT_TERESINA_WGS84
    layer_obj = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
    file_key, file_uri, layer_id, is_custom_layer = get_test_cache_variables(layer_obj, geo_extent)

    assert layer_id == 'EsaWorldCover__LandCoverClass_BUILT_UP__StartYear_2020_EndYear_2020.tif'
    assert is_custom_layer == False

def test_metric_with_start_end_date():
    zones = IDN_Jakarta_zone
    metric_obj = BuiltLandWithLowSurfaceReflectivity()
    file_key, file_uri, metric_id, is_custom_metric = get_test_cache_variables(metric_obj, zones)

    assert metric_id == 'BuiltLandWithLowSurfaceReflectivity__StartYear_2021_EndYear_2021.csv'
    assert is_custom_metric == False

