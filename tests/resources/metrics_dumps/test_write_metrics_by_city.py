import pytest

from city_metrix import *
from city_metrix.file_cache_config import set_cache_settings
from city_metrix.constants import cif_testing_s3_bucket_uri
from ..bbox_constants import GEOZONE_TERESINA_WGS84, GEOZONE_FLORIANOPOLIS_WGS84
from ..conftest import DUMP_RUN_LEVEL, DumpRunLevel
from ..tools import prep_output_path, verify_file_is_populated
from ...tools.general_tools import create_target_folder

ZONE = GEOZONE_TERESINA_WGS84
# ZONE = GEOZONE_FLORIANOPOLIS_WGS84

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_built_land_with_high_land_surface_temperature(target_folder):
    set_cache_settings(cif_testing_s3_bucket_uri, 'dev')
    geo_zone = ZONE
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)

    file_path = prep_output_path(target_metrics_folder, 'built_land_with_high_land_surface_temperature.geojson')
    BuiltLandWithHighLST().write_as_geojson(geo_zone, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_natural_areas_percent(target_folder):
    set_cache_settings(cif_testing_s3_bucket_uri, 'dev')
    geo_zone = ZONE
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)

    file_path = prep_output_path(target_metrics_folder, 'natural_areas_percent.geojson')
    NaturalAreasPercent().write_as_geojson(geo_zone, file_path)
    assert verify_file_is_populated(file_path)
