import time

import numpy as np
import pytest

from city_metrix import TreeCanopyHeight
from city_metrix.constants import CTCM_CACHE_S3_BUCKET_URI, DEFAULT_DEVELOPMENT_ENV, \
    ProjectionType, CTCM_PADDED_AOI_BUFFER, CIF_TESTING_S3_BUCKET_URI
from city_metrix.layers import OvertureBuildingsDSM, FabDEM, OpenUrban, AlbedoCloudMasked
from city_metrix.metrix_tools import get_projection_type
from tests.resources.conftest import DUMP_RUN_LEVEL, DumpRunLevel
from tests.resources.file_caching.bbox_urban_extents import GEOEXTENT_TERESINA_URBAN_EXTENT, \
    GEOEXTENT_FLORIANOPOLIS_URBAN_EXTENT, GEOEXTENT_CAPETOWN_BIZDISTRICT_EXTENT
from tests.test_layers import assert_raster_stats
from tests.resources.tools import _evaluate_bounds

TEST_BUCKET = CIF_TESTING_S3_BUCKET_URI # Default for testing
# TEST_BUCKET = CTCM_CACHE_S3_BUCKET_URI

# GEO_EXTENT = GEOEXTENT_TERESINA_URBAN_EXTENT # Default for testing
# GEO_EXTENT = GEOEXTENT_FLORIANOPOLIS_URBAN_EXTENT
GEO_EXTENT = GEOEXTENT_CAPETOWN_BIZDISTRICT_EXTENT

TERESINA_CITY_SUB_AREA = (739568,9432142, 741393,9433825)
FLORIANOPOLIS_CITY_SUB_AREA = (729496,6933650, 731047,6934496)
CAPETOWN_CITY_SUB_AREA = (260453,6242476, 261798,6243510 ) # EPSG: 32734

if GEO_EXTENT == GEOEXTENT_TERESINA_URBAN_EXTENT:
    SUB_AREA = TERESINA_CITY_SUB_AREA
elif GEO_EXTENT == GEOEXTENT_FLORIANOPOLIS_URBAN_EXTENT:
    SUB_AREA = FLORIANOPOLIS_CITY_SUB_AREA
else:
    SUB_AREA =CAPETOWN_CITY_SUB_AREA

# Full runtimes:
# Teresina ~15 mins
# Florianopolis 2 hours

# 8-10 min runtime for Teresina
# 46 mins for Florianopolis
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_dem_city():
    layer_obj = FabDEM()
    layer_obj.cache_city_data(bbox=GEO_EXTENT, s3_bucket=TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, aoi_buffer_m=CTCM_PADDED_AOI_BUFFER,
                              force_data_refresh=True, spatial_resolution=1)

    # pause to allow S3 to catch up
    time.sleep(60)

    data = layer_obj.retrieve_data(GEO_EXTENT, s3_bucket= TEST_BUCKET, aoi_buffer_m= CTCM_PADDED_AOI_BUFFER,
                                   s3_env=DEFAULT_DEVELOPMENT_ENV, city_aoi_modifier=SUB_AREA, spatial_resolution=1)
    assert np.size(data) > 0
    if GEO_EXTENT == GEOEXTENT_TERESINA_URBAN_EXTENT:
        assert_raster_stats(data, 1, 63.5, 96.2, 3071475, 0)
    elif GEO_EXTENT == GEOEXTENT_FLORIANOPOLIS_URBAN_EXTENT:
        assert_raster_stats(data, 1, 0.0, 12.4, 1312146, 0)
    elif GEO_EXTENT == GEOEXTENT_CAPETOWN_BIZDISTRICT_EXTENT:
        assert_raster_stats(data, 1, 6.30, 151.09, 1390730, 0)
    assert _evaluate_bounds(SUB_AREA, data)
    assert get_projection_type(data.rio.crs.to_epsg()) == ProjectionType.UTM

# 52 min runtime for Teresina
# 131 min Florianopolis
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_overture_buildings_dsm_city():
    layer_obj = OvertureBuildingsDSM()
    layer_obj.cache_city_data(bbox=GEO_EXTENT, s3_bucket=TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, aoi_buffer_m=CTCM_PADDED_AOI_BUFFER,
                              force_data_refresh=True, spatial_resolution=1)

    # pause to allow S3 to catch up
    time.sleep(60)

    data = layer_obj.retrieve_data(GEO_EXTENT, s3_bucket= TEST_BUCKET, aoi_buffer_m= CTCM_PADDED_AOI_BUFFER,
                                   s3_env=DEFAULT_DEVELOPMENT_ENV, city_aoi_modifier=SUB_AREA, spatial_resolution=1)
    assert np.size(data) > 0
    if GEO_EXTENT == GEOEXTENT_TERESINA_URBAN_EXTENT:
        assert_raster_stats(data, 1, 63.5, 96.2, 3071475, 0)
    elif GEO_EXTENT == GEOEXTENT_FLORIANOPOLIS_URBAN_EXTENT:
        assert_raster_stats(data, 1, 0.0, 12.4, 1312146, 0)
    elif GEO_EXTENT == GEOEXTENT_CAPETOWN_BIZDISTRICT_EXTENT:
        assert_raster_stats(data, 1, 6.30, 156.71, 1390730, 0)
    assert _evaluate_bounds(SUB_AREA, data)
    assert get_projection_type(data.rio.crs.to_epsg()) == ProjectionType.UTM


# # Note: LULC is derived from OpenUrban within CTCM

# # 4 min runtime for Teresina
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_open_urban_city():
    layer_obj = OpenUrban()
    layer_obj.cache_city_data(bbox=GEO_EXTENT, s3_bucket=TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, aoi_buffer_m=CTCM_PADDED_AOI_BUFFER,
                              force_data_refresh=True, spatial_resolution=1)

    # pause to allow S3 to catch up
    time.sleep(60)

    data = layer_obj.retrieve_data(GEO_EXTENT, s3_bucket= TEST_BUCKET, aoi_buffer_m= CTCM_PADDED_AOI_BUFFER,
                                   s3_env=DEFAULT_DEVELOPMENT_ENV, city_aoi_modifier=SUB_AREA, spatial_resolution=1)

    assert np.size(data) > 0
    if GEO_EXTENT == GEOEXTENT_TERESINA_URBAN_EXTENT:
        assert_raster_stats(data, 1, 110.0, 620.0, 3071475, 0)
    elif GEO_EXTENT == GEOEXTENT_FLORIANOPOLIS_URBAN_EXTENT:
        assert_raster_stats(data, 1, 110.0, 620.0, 1312146, 0)
    elif GEO_EXTENT == GEOEXTENT_CAPETOWN_BIZDISTRICT_EXTENT:
        assert_raster_stats(data, 2, 110.00, 620.00, 1390730, 0)
    assert _evaluate_bounds(SUB_AREA, data)
    assert get_projection_type(data.rio.crs.to_epsg()) == ProjectionType.UTM

# 7 min runtime for Teresina
# 26 min Florianopolis
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_tree_canopy_height_city():
    layer_obj = TreeCanopyHeight()
    layer_obj.cache_city_data(bbox=GEO_EXTENT, s3_bucket=TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, aoi_buffer_m=CTCM_PADDED_AOI_BUFFER,
                              force_data_refresh=True, spatial_resolution=1)

    # pause to allow S3 to catch up
    time.sleep(60)

    data = layer_obj.retrieve_data(GEO_EXTENT, s3_bucket= TEST_BUCKET, aoi_buffer_m= CTCM_PADDED_AOI_BUFFER,
                                   s3_env=DEFAULT_DEVELOPMENT_ENV, city_aoi_modifier=SUB_AREA, spatial_resolution=1)

    assert np.size(data) > 0
    if GEO_EXTENT == GEOEXTENT_TERESINA_URBAN_EXTENT:
        assert_raster_stats(data, 1, 0.0, 20.0, 3071475, 0)
    elif GEO_EXTENT == GEOEXTENT_FLORIANOPOLIS_URBAN_EXTENT:
        assert_raster_stats(data, 1, 0.0, 27.0, 1312146, 0)
    elif GEO_EXTENT == GEOEXTENT_CAPETOWN_BIZDISTRICT_EXTENT:
        assert_raster_stats(data, 1, 0.00, 18.00, 1390730, 0)
    assert _evaluate_bounds(SUB_AREA, data)
    assert get_projection_type(data.rio.crs.to_epsg()) == ProjectionType.UTM

# 10 min runtime for Teresina
# 38-41 min Florianopolis
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_albedo_cloud_mask_city():
    layer_obj = AlbedoCloudMasked()
    layer_obj.cache_city_data(bbox=GEO_EXTENT, s3_bucket=TEST_BUCKET, s3_env=DEFAULT_DEVELOPMENT_ENV, aoi_buffer_m=CTCM_PADDED_AOI_BUFFER,
                              force_data_refresh=True, spatial_resolution=1)

    # pause to allow S3 to catch up
    time.sleep(60)

    data = layer_obj.retrieve_data(GEO_EXTENT, s3_bucket= TEST_BUCKET, aoi_buffer_m= CTCM_PADDED_AOI_BUFFER,
                                   s3_env=DEFAULT_DEVELOPMENT_ENV, city_aoi_modifier=SUB_AREA, spatial_resolution=1)

    assert np.size(data) > 0
    if GEO_EXTENT == GEOEXTENT_TERESINA_URBAN_EXTENT:
        assert_raster_stats(data, 1, 0.11, 0.68, 3071475, 0)
    elif GEO_EXTENT == GEOEXTENT_FLORIANOPOLIS_URBAN_EXTENT:
        assert_raster_stats(data, 1, 0.03, 0.47, 1312146, 0)
    elif GEO_EXTENT == GEOEXTENT_CAPETOWN_BIZDISTRICT_EXTENT:
        assert_raster_stats(data, 1, 0.03, 0.65, 1390730, 0)
    assert _evaluate_bounds(SUB_AREA, data)
    assert get_projection_type(data.rio.crs.to_epsg()) == ProjectionType.UTM

