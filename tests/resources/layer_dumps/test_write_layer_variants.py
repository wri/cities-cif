# This code is mostly intended for manual execution
# Execution configuration is specified in the conftest file
from datetime import datetime

import pytest
import xarray as xr

from city_metrix.constants import cif_testing_s3_bucket_uri
from city_metrix.file_cache_config import set_cache_settings, clear_cache_settings
from city_metrix.layers import *
from city_metrix.metrix_dao import get_layer_cache_variables, check_if_cache_file_exists
from tests.resources.bbox_constants import GEOEXTENT_TERESINA_WGS84, GEOEXTENT_TERESINA_UTM, BBOX_USA_OR_PORTLAND_2
from tests.resources.conftest import DUMP_RUN_LEVEL, DumpRunLevel
from tests.resources.tools import get_test_bbox, cleanup_cache_files, prep_output_path, verify_file_is_populated, \
    get_file_count_in_folder
from tests.tools.general_tools import get_class_default_spatial_resolution

# ============ TEST WRITE TO S3 CACHE, READ FROM S3 CACHE =====================
CACHE_TO_S3 = True

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_geotiff_layer_caching(target_folder):
    layer_obj = VegetationWaterMap()
    _cache_write_read(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_geojson_layer_caching(target_folder):
    layer_obj = OpenStreetMap(osm_class=OpenStreetMapClass.ROAD)
    _cache_write_read(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_netcdf_layer_caching(target_folder):
    layer_obj = Era5HottestDay()
    _cache_write_read(layer_obj, target_folder)

# ==================== Test resolution changes ===========================
# Multiplier applied to the default spatial_resolution of the layer
# Use value of 1 for default resolution.
RESOLUTION_MTHD = 'multiplier'
# RESOLUTION_MTHD = 'fixed'
RESOLUTION_MULTIPLIER = 2
FIXED_RESOLUTION = 30 # Note: Some layers do not support less than resolution of 30m

BBOX = BBOX_USA_OR_PORTLAND_2

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_alos_dsm(target_folder):
    file_path = prep_output_path(target_folder, 'AlosDSM_targeted_resolution.tif')
    target_resolution = get_test_resolution(AlosDSM())
    bbox = get_test_bbox(BBOX)
    AlosDSM().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_nasa_dem(target_folder):
    file_path = prep_output_path(target_folder, 'NasaDEM_targeted_resolution.tif')
    target_resolution = get_test_resolution(NasaDEM())
    bbox = get_test_bbox(BBOX)
    NasaDEM().write(bbox, file_path, spatial_resolution=target_resolution)
    assert verify_file_is_populated(file_path)


# ==================== Other tests ===========================
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_albedo_tiled_unbuffered(target_folder):
    file_path = prep_output_path(target_folder, 'Albedo_tiled_unbuffered.tif')
    target_resolution = get_test_resolution(Albedo())
    bbox = get_test_bbox(BBOX)
    (Albedo()
     .write(bbox, file_path, tile_side_length=0.01, buffer_size=None, length_units="degrees",
            spatial_resolution=target_resolution))
    file_count = get_file_count_in_folder(file_path)

    expected_file_count = 3 # includes 2 tiles and one json file
    assert file_count == expected_file_count

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_albedo_tiled_buffered(target_folder):
    buffer_degrees = 0.001
    file_path = prep_output_path(target_folder, 'Albedo_tiled_buffered.tif')
    target_resolution = get_test_resolution(Albedo())
    bbox = get_test_bbox(BBOX)
    (Albedo()
     .write(bbox, file_path, tile_side_length=0.01, buffer_size=buffer_degrees, length_units="degrees",
            spatial_resolution=target_resolution))
    file_count = get_file_count_in_folder(file_path)

    expected_file_count = 4 # includes 2 tiles and two json files
    assert file_count == expected_file_count


@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_nasa_dem_tiled_unbuffered(target_folder):
    file_path = prep_output_path(target_folder, 'NasaDEM_tiled_unbuffered.tif')
    target_resolution = get_test_resolution(NasaDEM())
    bbox = get_test_bbox(BBOX)
    (NasaDEM()
     .write(bbox, file_path,
            tile_side_length=.008, length_units='degrees',
            spatial_resolution=target_resolution, resampling_method='bilinear'))

    file_count = get_file_count_in_folder(file_path)
    expected_file_count = 5 # includes 4 tiles and 1 json files
    assert file_count == expected_file_count


@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_get_nasa_dem_bicubic(target_folder):
    utm_bbox = get_test_bbox(BBOX).as_utm_bbox()
    data = NasaDEM().get_data(utm_bbox, spatial_resolution=30, resampling_method='bicubic')

    assert isinstance(data, xr.DataArray)
    assert data.crs == utm_bbox.crs

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_nasa_dem(target_folder):
    set_cache_settings(cif_testing_s3_bucket_uri, 'dev')
    file_path = prep_output_path(target_folder, 'NasaDEM_small_city_wgs84.tif')
    bbox = get_test_bbox(GEOEXTENT_TERESINA_WGS84)
    NasaDEM().write(bbox, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_nasa_dem_utm(target_folder):
    set_cache_settings(cif_testing_s3_bucket_uri, 'dev')
    file_path = prep_output_path(target_folder, 'NasaDEM_small_city_utm.tif')
    bbox = get_test_bbox(GEOEXTENT_TERESINA_UTM)
    NasaDEM().write(bbox, file_path)
    assert verify_file_is_populated(file_path)

def _cache_write_read(layer_obj, target_folder):
    if CACHE_TO_S3:
        set_cache_settings(cif_testing_s3_bucket_uri, 'dev')
        cache_scheme = 's3'
    else:
        set_cache_settings(f"file://{target_folder}", 'dev')
        cache_scheme = 'file'
    geo_extent = get_test_bbox(GEOEXTENT_TERESINA_WGS84)
    file_key, file_uri, layer_id = get_layer_cache_variables(layer_obj, geo_extent)

    os_file_path = prep_output_path(target_folder, layer_id)
    cleanup_cache_files(cache_scheme, file_key, os_file_path)
    try:
        start_time = datetime.now()
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        cache_write_time = _get_time_difference_to_now_seconds(start_time)
        cache_file_exists = check_if_cache_file_exists(file_uri)
        assert cache_file_exists, "Test failed since file did not upload to s3"
        if cache_file_exists:
            start_time = datetime.now()
            layer_obj.write(bbox=geo_extent, output_path=os_file_path)
            cache_read_time = _get_time_difference_to_now_seconds(start_time)
            assert verify_file_is_populated(os_file_path)
        else:
            cache_read_time = None
    finally:
        cleanup_cache_files(cache_scheme, file_key, os_file_path)
        clear_cache_settings()

    print(f"\ncache_write_secs: {cache_write_time}, cache_read_secs: {cache_read_time}")
    assert cache_write_time >= cache_read_time, f"Cache-write time {cache_write_time} was not longer than cache-read time {cache_read_time}."

def _get_time_difference_to_now_seconds(start_time):
    end_time = datetime.now()
    diff_seconds = (end_time - start_time).total_seconds()
    return diff_seconds

def get_test_resolution(cls):
    if RESOLUTION_MTHD == 'fixed':
        target_res = FIXED_RESOLUTION
    else:
        target_res = RESOLUTION_MULTIPLIER * get_class_default_spatial_resolution(cls)
    return target_res