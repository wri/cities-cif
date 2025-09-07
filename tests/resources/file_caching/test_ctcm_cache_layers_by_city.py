import tempfile
import time
import numpy as np
import pytest

from city_metrix.metrix_dao import write_layer
from city_metrix.constants import DEFAULT_DEVELOPMENT_ENV, CIF_TESTING_S3_BUCKET_URI, CTCM_CACHE_S3_BUCKET_URI, \
    GTIFF_FILE_EXTENSION, ProjectionType
from city_metrix.layers import OpenUrban
from city_metrix.metrix_tools import get_projection_type
from tests.resources.conftest import DUMP_RUN_LEVEL, DumpRunLevel
from tests.resources.file_caching.bbox_urban_extents import GEOEXTENT_TERESINA_URBAN_EXTENT, \
    GEOEXTENT_FLORIANOPOLIS_URBAN_EXTENT
from tests.resources.tools import _evaluate_bounds
from tests.test_layers import assert_raster_stats

TEST_BUCKET = CIF_TESTING_S3_BUCKET_URI # Default for testing

SAVE_RESULTS_TO_OS = False # False is default

TERESINA_CITY_SUB_AREA = (739568,9432142, 741393,9433825)
FLORIANOPOLIS_CITY_SUB_AREA = (729496,6933650, 731047,6934496)

temp_dir = tempfile.gettempdir()
OUTPUT_FILE_ROOT = rf'file://{temp_dir}/test_result_tif_files/ctcm_test_result'


@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_openurban_city_teresina():
    layer_obj = OpenUrban()
    geo_extent = GEOEXTENT_TERESINA_URBAN_EXTENT
    layer_obj.cache_city_data(bbox=geo_extent, s3_bucket=TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, force_data_refresh=True, spatial_resolution=1)

    # pause to allow S3 to catch up
    time.sleep(100)

    data = layer_obj.retrieve_data(geo_extent, s3_bucket= TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, city_aoi_modifier=TERESINA_CITY_SUB_AREA,
                                 spatial_resolution=1)
    if SAVE_RESULTS_TO_OS and np.size(data) > 0:
        write_layer(data, fr'{OUTPUT_FILE_ROOT}/{geo_extent.city_id}_openurban_test_teresina.tif', GTIFF_FILE_EXTENSION)

    assert np.size(data) > 0
    assert_raster_stats(data, 1, 110.0, 620.0, 3071475, 0)
    assert get_projection_type(data.rio.crs.to_epsg()) == ProjectionType.UTM
    assert _evaluate_bounds(TERESINA_CITY_SUB_AREA, data)


@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_openurban_city_florianopolis():
    layer_obj = OpenUrban()
    geo_extent = GEOEXTENT_FLORIANOPOLIS_URBAN_EXTENT
    layer_obj.cache_city_data(bbox=geo_extent, s3_bucket=TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, force_data_refresh=True, spatial_resolution=1)

    # pause to allow S3 to catch up
    time.sleep(100)

    data = layer_obj.retrieve_data(geo_extent, s3_bucket= TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, city_aoi_modifier=FLORIANOPOLIS_CITY_SUB_AREA,
                                 spatial_resolution=1)
    if SAVE_RESULTS_TO_OS and np.size(data) > 0:
        write_layer(data, fr'{OUTPUT_FILE_ROOT}/{geo_extent.city_id}_openurban_test_florianopolis.tif', GTIFF_FILE_EXTENSION)

    assert np.size(data) > 0
    assert_raster_stats(data, 1, 110.0, 620.0, 1312146, 0)
    assert get_projection_type(data.rio.crs.to_epsg()) == ProjectionType.UTM
    assert _evaluate_bounds(FLORIANOPOLIS_CITY_SUB_AREA, data)

