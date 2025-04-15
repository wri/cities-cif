import pytest
import timeout_decorator

from city_metrix.file_cache_config import set_cache_settings, clear_cache_settings
from city_metrix.constants import cif_testing_s3_bucket_uri
from city_metrix.layers import *
from city_metrix.layers.layer_dao import get_cache_variables, check_if_cache_file_exists
from tests.resources.tools import get_test_bbox, cleanup_cache_files, prep_output_path
from ..bbox_constants import GEOEXTENT_TERESINA_WGS84
from ..conftest import DUMP_RUN_LEVEL, DumpRunLevel

PRESERVE_RESULTS_ON_OS = True
SLOW_TEST_TIMEOUT_SECONDS = 300 # 300 seconds = 5 minutes

PROCESSING_CITY = GEOEXTENT_TERESINA_WGS84
CITY_UT_NAME = 'teresina'

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_AcagPM2p5_write_by_city(target_folder):
    layer_obj = AcagPM2p5()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_Albedo_write_by_city(target_folder):
    layer_obj = Albedo(start_date='2021-01-01', end_date='2021-12-31')
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_AlosDSM_write_by_city(target_folder):
    layer_obj = AlosDSM()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_AqueductFlood_write_by_city(target_folder):
    layer_obj = AqueductFlood()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_AverageNetBuildingHeight_write_by_city(target_folder):
    layer_obj = AverageNetBuildingHeight()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_BuiltUpHeight_write_by_city(target_folder):
    layer_obj = BuiltUpHeight()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_CamsGhg_write_by_city(target_folder):
    layer_obj = CamsGhg()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_Cams_write_by_city(target_folder):
    layer_obj = Cams()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_Era5HottestDay_write_by_city(target_folder):
    layer_obj = Era5HottestDay()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_EsaWorldCover_write_by_city(target_folder):
    layer_obj = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP,year=2020)
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_HeightAboveNearestDrainage_write_by_city(target_folder):
    layer_obj = HeightAboveNearestDrainage()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_HighLandSurfaceTemperature_write_by_city(target_folder):
    layer_obj = HighLandSurfaceTemperature()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_HighSlope_write_by_city(target_folder):
    layer_obj = HighSlope()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_ImperviousSurface_write_by_city(target_folder):
    layer_obj = ImperviousSurface()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_LandCoverGlad_write_by_city(target_folder):
    layer_obj = LandCoverGlad(year=2020)
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_LandCoverSimplifiedGlad_write_by_city(target_folder):
    layer_obj = LandCoverSimplifiedGlad(year=2020)
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_LandCoverHabitatGlad_write_by_city(target_folder):
    layer_obj = LandCoverHabitatGlad(year=2020)
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_LandCoverHabitatChangeGlad_write_by_city(target_folder):
    layer_obj = LandCoverHabitatChangeGlad(start_year=2000, end_year=2020)
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_LandSurfaceTemperature_write_by_city(target_folder):
    layer_obj = LandSurfaceTemperature(start_date='2022-01-01', end_date='2022-12-31')
    _run_write_layers_by_city_test(layer_obj, target_folder)

# # TODO Determine how to write out file from temporal dataset
# @pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
# def test_LandsatCollection2_write_by_city(target_folder):
#     layer_obj = LandsatCollection2(bands=['red', 'green', 'blue'], start_date='2022-01-01', end_date='2022-12-31')
#     _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_NasaDEM_write_by_city(target_folder):
    layer_obj = NasaDEM()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_NaturalAreas_write_by_city(target_folder):
    layer_obj = NaturalAreas()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_NdviSentinel2_write_by_city(target_folder):
    layer_obj = NdviSentinel2(year=2020)
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_OpenBuildings_write_by_city(target_folder):
    layer_obj = OpenBuildings()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_OpenStreetMap_write_by_city(target_folder):
    layer_obj = OpenStreetMap(osm_class=OpenStreetMapClass.OPEN_SPACE)
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_OvertureBuildings_write_by_city(target_folder):
    layer_obj = OvertureBuildings()
    _run_write_layers_by_city_test(layer_obj, target_folder)

# TODO Very slow processing
@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_OvertureBuildingsHeight_write_by_city(target_folder):
    layer_obj = OvertureBuildingsHeight(CITY_UT_NAME)
    _run_write_layers_by_city_test(layer_obj, target_folder)

# TODO Very slow processing
@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_OvertureBuildingsHeightRaster_write_by_city(target_folder):
    layer_obj = OvertureBuildingsHeightRaster(CITY_UT_NAME)
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_PopWeightedPM2p5_write_by_city(target_folder):
    layer_obj = PopWeightedPM2p5()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_ProtectedAreas_write_by_city(target_folder):
    layer_obj = ProtectedAreas()
    _run_write_layers_by_city_test(layer_obj, target_folder)

# # TODO test fails due to https://gfw.atlassian.net/browse/CDB-243
# @pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
# def test_RiparianAreas_write_by_city(target_folder):
#     layer_obj = RiparianAreas()
#     _run_write_layers_by_city_test(layer_obj, target_folder)

# # TODO Determine how to write out file from temporal dataset
# @pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
# def test_Sentinel2Level2_write_by_city(target_folder):
#     layer_obj = Sentinel2Level2(bands=['blue'], start_date='2022-01-01', end_date='2022-12-31')
#     _run_write_layers_by_city_test(layer_obj, target_folder)

# TODO Very slow processing
# TODO Run fails. Appears to be a memory issue
@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_SmartSurfaceLULC_write_by_city(target_folder):
    layer_obj = SmartSurfaceLULC()
    _run_write_layers_by_city_test(layer_obj, target_folder)

# # TODO Very slow processing. Long runtime can cause failure for larger city
@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_TreeCanopyHeight_write_by_city(target_folder):
    layer_obj = TreeCanopyHeight()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_TreeCanopyCoverMask_write_by_city(target_folder):
    layer_obj = TreeCanopyCoverMask()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_TreeCover_write_by_city(target_folder):
    layer_obj = TreeCover()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_UrbanExtents_write_by_city(target_folder):
    layer_obj = UrbanExtents(year=2020)
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_UrbanLandUse_write_by_city(target_folder):
    layer_obj = UrbanLandUse()
    _run_write_layers_by_city_test(layer_obj, target_folder)

# # TODO Very slow processing
@timeout_decorator.timeout(SLOW_TEST_TIMEOUT_SECONDS)
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_UtGlobus_write_by_city(target_folder):
    layer_obj = UtGlobus(CITY_UT_NAME)
    _run_write_layers_by_city_test(layer_obj, target_folder)

# TODO Fails for:  # layer_obj = VegetationWaterMap(start_date='2020-01-01', end_date='2020-12-31')
@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_SLOW_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_VegetationWaterMap_write_by_city(target_folder):
    layer_obj = VegetationWaterMap()
    _run_write_layers_by_city_test(layer_obj, target_folder)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since TEST_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_WorldPop_write_by_city(target_folder):
    layer_obj = WorldPop()
    _run_write_layers_by_city_test(layer_obj, target_folder)



def _run_write_layers_by_city_test(layer_obj, target_folder):
    set_cache_settings(cif_testing_s3_bucket_uri, 'dev')
    cache_scheme = 's3'
    geo_extent = get_test_bbox(PROCESSING_CITY)
    file_key, file_uri, layer_id = get_cache_variables(layer_obj, geo_extent)

    os_file_path = prep_output_path(target_folder, layer_id)
    cleanup_cache_files(cache_scheme, file_key, os_file_path)
    try:
        layer_obj.write(bbox=geo_extent, output_path=file_uri)
        cache_file_exists = check_if_cache_file_exists(file_uri)
        assert cache_file_exists, "Test failed since file did not upload to s3"
        if cache_file_exists and PRESERVE_RESULTS_ON_OS:
            layer_obj.write(bbox=geo_extent, output_path=os_file_path)
    finally:
        cleanup_os_file_path = None if PRESERVE_RESULTS_ON_OS else os_file_path
        cleanup_cache_files(cache_scheme, file_key, cleanup_os_file_path)
        clear_cache_settings()
