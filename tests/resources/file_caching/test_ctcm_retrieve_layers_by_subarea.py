import math
import numpy as np
import pytest

from city_metrix import TreeCanopyHeight
from city_metrix.constants import DEFAULT_DEVELOPMENT_ENV, ProjectionType, GTIFF_FILE_EXTENSION, \
    CIF_TESTING_S3_BUCKET_URI
from city_metrix.layers import OvertureBuildingsDSM, FabDEM, OpenUrban, AlbedoCloudMasked
from city_metrix.metrix_dao import write_layer
from city_metrix.metrix_tools import get_projection_type
from tests.resources.bbox_constants import GEOEXTENT_TERESINA, GEOEXTENT_FLORIANOPOLIS
from tests.resources.conftest import DumpRunLevel, DUMP_RUN_LEVEL
from tests.test_layers import assert_raster_stats

TEST_BUCKET = CIF_TESTING_S3_BUCKET_URI

SAVE_RESULTS_TO_OS = False # False is default

# GEO_EXTENT = GEOEXTENT_FLORIANOPOLIS
# CITY_SUB_AREA = (729496,6933650, 731047,6934496)
GEO_EXTENT = GEOEXTENT_TERESINA
CITY_SUB_AREA = (740102,9424381, 742071,9425993) # Teresina
#

# For full caching:
# 8-10 min runtime for Teresina
# 46 mins for Florianopolis
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_get_fabdem_city():
    layer_obj = FabDEM()
    data = layer_obj.retrieve_data(GEO_EXTENT, s3_bucket= TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, city_aoi_modifier=CITY_SUB_AREA,
                                 spatial_resolution=1)
    if SAVE_RESULTS_TO_OS and np.size(data) > 0:
        write_layer(data, fr'file:////tmp/test_result_tif_files/ctcm_test_result/{GEO_EXTENT.city_id}_fabdem_test.tif', GTIFF_FILE_EXTENSION)

    assert np.size(data) > 0
    if GEO_EXTENT == GEOEXTENT_FLORIANOPOLIS:
        assert_raster_stats(data, 1, 0.0, 12.4, 1312146, 0)
    elif GEO_EXTENT == GEOEXTENT_TERESINA:
        assert_raster_stats(data, 1, 62.9, 85.5, 3174028, 0)
    assert get_projection_type(data.rio.crs.to_epsg()) == ProjectionType.UTM
    assert _evaluate_bounds(CITY_SUB_AREA, data)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_get_open_urban_city():
    layer_obj = OpenUrban()
    data = layer_obj.retrieve_data(GEO_EXTENT, s3_bucket= TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, city_aoi_modifier=CITY_SUB_AREA,
                                 spatial_resolution=1)
    if SAVE_RESULTS_TO_OS and np.size(data) > 0:
        write_layer(data, fr'file:////tmp/test_result_tif_files/ctcm_test_result/{GEO_EXTENT.city_id}_openurban_test.tif', GTIFF_FILE_EXTENSION)

    assert np.size(data) > 0
    if GEO_EXTENT == GEOEXTENT_FLORIANOPOLIS:
        assert_raster_stats(data, 1, 110.0, 620.0, 1312146, 0)
    elif GEO_EXTENT == GEOEXTENT_TERESINA:
        assert_raster_stats(data, 1, 110.0, 600.0, 3174028, 0)
    assert get_projection_type(data.rio.crs.to_epsg()) == ProjectionType.UTM
    assert _evaluate_bounds(CITY_SUB_AREA, data)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_get_tree_canopy_height_city():
    layer_obj = TreeCanopyHeight()
    data = layer_obj.retrieve_data(GEO_EXTENT, s3_bucket= TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, city_aoi_modifier=CITY_SUB_AREA,
                                 spatial_resolution=1)
    if SAVE_RESULTS_TO_OS and np.size(data) > 0:
        write_layer(data, fr'file:////tmp/test_result_tif_files/ctcm_test_result/{GEO_EXTENT.city_id}_treecanopy_test.tif', GTIFF_FILE_EXTENSION)

    assert np.size(data) > 0
    if GEO_EXTENT == GEOEXTENT_FLORIANOPOLIS:
        assert_raster_stats(data, 1, 0.0, 27.0, 1312146, 0)
    elif GEO_EXTENT == GEOEXTENT_TERESINA:
        assert_raster_stats(data, 1, 0.0, 19.0, 3174028, 0)
    assert get_projection_type(data.rio.crs.to_epsg()) == ProjectionType.UTM
    assert _evaluate_bounds(CITY_SUB_AREA, data)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_get_albedo_cloud_mask_city():
    layer_obj = AlbedoCloudMasked()
    data = layer_obj.retrieve_data(GEO_EXTENT, s3_bucket= TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, city_aoi_modifier=CITY_SUB_AREA,
                                 spatial_resolution=1)
    if SAVE_RESULTS_TO_OS and np.size(data) > 0:
        write_layer(data, fr'file:////tmp/test_result_tif_files/ctcm_test_result/{GEO_EXTENT.city_id}_albedocloudmask_test.tif', GTIFF_FILE_EXTENSION)

    assert np.size(data) > 0
    if GEO_EXTENT == GEOEXTENT_FLORIANOPOLIS:
        assert_raster_stats(data, 1, 0.03, 0.47, 1312146, 0)
    elif GEO_EXTENT == GEOEXTENT_TERESINA:
        assert_raster_stats(data, 1, 0.08, 0.31, 3174028, 0)
    assert get_projection_type(data.rio.crs.to_epsg()) == ProjectionType.UTM
    assert _evaluate_bounds(CITY_SUB_AREA, data)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_get_overture_buildings_dsm_city():
    layer_obj = OvertureBuildingsDSM()
    data = layer_obj.retrieve_data(GEO_EXTENT, s3_bucket= TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, city_aoi_modifier=CITY_SUB_AREA,
                                 spatial_resolution=1)
    if SAVE_RESULTS_TO_OS and np.size(data) > 0:
        write_layer(data, fr'file:////tmp/test_result_tif_files/ctcm_test_result/{GEO_EXTENT.city_id}_overturedsm_test.tif', GTIFF_FILE_EXTENSION)

    assert np.size(data) > 0
    if GEO_EXTENT == GEOEXTENT_FLORIANOPOLIS:
        assert_raster_stats(data, 1, 0.0, 12.4, 1312146, 0)
    elif GEO_EXTENT == GEOEXTENT_TERESINA:
        assert_raster_stats(data, 1, 62.9, 92.7, 3174028, 0)
    assert get_projection_type(data.rio.crs.to_epsg()) == ProjectionType.UTM
    assert _evaluate_bounds(CITY_SUB_AREA, data)


def _evaluate_bounds(expected_bounds, data):
    min_x = math.floor(data["x"].min().item())
    max_x = math.ceil(data["x"].max().item())
    min_y = math.floor(data["y"].min().item())
    max_y = math.ceil(data["y"].max().item())
    actual_bounds = (min_x, min_y, max_x, max_y)
    return actual_bounds==expected_bounds
