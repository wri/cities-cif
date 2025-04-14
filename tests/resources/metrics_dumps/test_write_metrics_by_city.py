import pytest

from city_metrix import *
from city_metrix.file_cache_config import set_cache_settings
from city_metrix.constants import cif_testing_s3_bucket_uri
from ..bbox_constants import GEOZONE_TERESINA_WGS84
from ..conftest import DUMP_RUN_LEVEL, DumpRunLevel
from ..tools import prep_output_path


@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_built_land_with_high_land_surface_temperature_os(target_folder):
    set_cache_settings(cif_testing_s3_bucket_uri, 'dev')
    file_path = prep_output_path(target_folder, 'built_land_with_high_land_surface_temperature.geojson')
    geo_zone = GEOZONE_TERESINA_WGS84
    BuiltLandWithHighLST().write_as_geojson(geo_zone, file_path)

