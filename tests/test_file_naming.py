from city_metrix import BuiltLandWithLowSurfaceReflectivity__Percent
from city_metrix.constants import CIF_TESTING_S3_BUCKET_URI
from city_metrix.layers import Albedo, AcagPM2p5, LandCoverHabitatChangeGlad, EsaWorldCover, EsaWorldCoverClass, Cams, \
    AqueductFlood
from tests.resources.bbox_constants import GEOEXTENT_TERESINA
from tests.resources.metrics_dumps.test_write_metric_variants import IDN_Jakarta_zone
from tests.tools.general_tools import get_test_cache_variables


def test_default_name_for_default_name_for_layer_with_year():
    geo_extent = GEOEXTENT_TERESINA
    layer_obj = AcagPM2p5()
    _, _, layer_id, is_custom_layer = get_test_cache_variables(layer_obj, geo_extent, CIF_TESTING_S3_BUCKET_URI)

    assert is_custom_layer == False
    assert layer_id == 'AcagPM2p5__StartYear_2022_EndYear_2022.tif'

def test_default_name_for_layer_with_start_end_years():
    geo_extent = GEOEXTENT_TERESINA
    layer_obj = LandCoverHabitatChangeGlad()
    _, _, layer_id, is_custom_layer = get_test_cache_variables(layer_obj, geo_extent, CIF_TESTING_S3_BUCKET_URI)

    assert is_custom_layer == False
    assert layer_id == 'LandCoverHabitatChangeGlad__StartYear_2000_EndYear_2020.tif'

def test_default_name_for_layer_with_start_end_dates_in_same_year():
    geo_extent = GEOEXTENT_TERESINA
    layer_obj = Cams()
    _, _, layer_id, is_custom_layer = get_test_cache_variables(layer_obj, geo_extent, CIF_TESTING_S3_BUCKET_URI)

    assert is_custom_layer == False
    assert layer_id == 'Cams__StartYear_2023_EndYear_2023.nc'

def test_default_name_for_layer_with_major_name():
    geo_extent = GEOEXTENT_TERESINA
    layer_obj = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
    _, _, layer_id, is_custom_layer = get_test_cache_variables(layer_obj, geo_extent, CIF_TESTING_S3_BUCKET_URI)

    assert is_custom_layer == False
    assert layer_id == 'EsaWorldCover__LandCoverClass_BUILT_UP__StartYear_2020_EndYear_2020.tif'

def test_default_name_for_metric_with_start_end_dates():
    zones = IDN_Jakarta_zone
    metric_obj = BuiltLandWithLowSurfaceReflectivity__Percent()
    file_key, file_uri, metric_id, is_custom_metric = get_test_cache_variables(metric_obj, zones, CIF_TESTING_S3_BUCKET_URI)

    assert is_custom_metric == False
    assert metric_id == 'BuiltLandWithLowSurfaceReflectivity__Percent__StartYear_2021_EndYear_2021.csv'


def test_custom_name_for_layer_with_start_end_dates():
    geo_extent = GEOEXTENT_TERESINA
    layer_obj = Albedo(start_date='2023-01-01', end_date='2023-12-31', threshold=0.2)
    _, _, layer_id, is_custom_layer = get_test_cache_variables(layer_obj, geo_extent, CIF_TESTING_S3_BUCKET_URI)

    assert is_custom_layer == True
    assert layer_id == 'Albedo__Threshold_02__StartDate_2023-01-01_EndDate_2023-12-31.tif'

def test_custom_name_for_layer_with_one_custom_minor_param():
    geo_extent = GEOEXTENT_TERESINA
    layer_obj = AqueductFlood(return_period_c="rp0002")
    _, _, layer_id, is_custom_layer = get_test_cache_variables(layer_obj, geo_extent, CIF_TESTING_S3_BUCKET_URI)

    assert is_custom_layer == True
    assert layer_id == 'AqueductFlood__ReturnPeriodC_rp0002__StartYear_2050_EndYear_2050.tif'

def test_custom_name_for_layer_with_two_custom_minor_param():
    geo_extent = GEOEXTENT_TERESINA
    layer_obj = AqueductFlood(return_period_c="rp0002", return_period_r="rp00002")
    _, _, layer_id, is_custom_layer = get_test_cache_variables(layer_obj, geo_extent, CIF_TESTING_S3_BUCKET_URI)

    assert is_custom_layer == True
    assert layer_id == 'AqueductFlood__ReturnPeriodC_rp0002__ReturnPeriodR_rp00002__StartYear_2050_EndYear_2050.tif'
