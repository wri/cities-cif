import tempfile
import numpy as np
import pytest

from city_metrix import BuiltLandWithHighLST__Percent
from city_metrix.metrix_dao import write_layer
from city_metrix.constants import DEFAULT_DEVELOPMENT_ENV, CIF_TESTING_S3_BUCKET_URI, GTIFF_FILE_EXTENSION
from tests.resources.conftest import DUMP_RUN_LEVEL, DumpRunLevel
from tests.resources.file_caching.bbox_urban_extents import GEOZONE_TERESINA_CITY_ADMiN_LEVEL

TEST_BUCKET = CIF_TESTING_S3_BUCKET_URI # Default for testing

SAVE_RESULTS_TO_OS = False # False is default

TERESINA_CITY_SUB_AREA = (739568,9432142, 741393,9433825)
FLORIANOPOLIS_CITY_SUB_AREA = (729496,6933650, 731047,6934496)

temp_dir = tempfile.gettempdir()
OUTPUT_FILE_ROOT = rf'file://{temp_dir}/test_result_tif_files/ctcm_test_result'
AOI_BUFFER_M = 0 # Do not buffer for test


@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_builtlandwithhightlst_city_teresina():
    metric_obj = BuiltLandWithHighLST__Percent()
    geo_zone = GEOZONE_TERESINA_CITY_ADMiN_LEVEL
    metric_obj.cache_city_metric(geo_zone=geo_zone, s3_bucket=TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, force_data_refresh=True)

    data = metric_obj.retrieve_metric(geo_zone, s3_bucket= TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV)
    if SAVE_RESULTS_TO_OS and np.size(data) > 0:
        write_layer(data, fr'{OUTPUT_FILE_ROOT}/{geo_zone.city_id}_builtlandwithhighlst_test_teresina.tif', GTIFF_FILE_EXTENSION)

    assert np.size(data) > 0
    assert len(data) == 138
