# This code is mostly intended for manual execution
# Execution configuration is specified in the conftest file
import geopandas as gpd
import pytest

from city_metrix.constants import WGS_CRS, CIF_TESTING_S3_BUCKET_URI, DEFAULT_DEVELOPMENT_ENV
from city_metrix.metrics import *
from tests.resources.bbox_constants import GEOZONE_FLORIANOPOLIS
from tests.resources.conftest import DUMP_RUN_LEVEL, DumpRunLevel
from tests.resources.tools import prep_output_path, verify_file_is_populated, cleanup_cache_files

from shapely.geometry import Polygon

jakarta_crude_boundary = \
    [(106.688353778504393, -6.095658595454545), (106.971210221495596, -6.089509542346041),
     (106.972088657653956, -6.197557189824047), (106.907084381935476, -6.37412285765396),
     (106.796401425982395, -6.367973804545455), (106.690989086979457, -6.165055051964809),
     (106.688353778504393, -6.095658595454545)]

IDN_Jakarta_zone = GeoZone(gpd.GeoDataFrame([Polygon(jakarta_crude_boundary)], columns=["geometry"])
                           .set_crs(WGS_CRS)
                           .reset_index())

ZONE = GEOZONE_FLORIANOPOLIS


@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_large_city(target_folder):
    file_path = prep_output_path(target_folder, 'metric', 'natural_areas__percent.geojson')
    NaturalAreas__Percent().write_as_geojson(ZONE, target_file_path=file_path)
    assert verify_file_is_populated(file_path)
    cleanup_cache_files(None, None, None, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_polygonal_zones(target_folder):
    zone = IDN_Jakarta_zone
    file_path = prep_output_path(target_folder, 'metric', 'IDN_Jakarta_natural_areas_polygon.geojson')

    NaturalAreas__Percent().write_as_geojson(zone, target_file_path=file_path)
    assert verify_file_is_populated(file_path)

    indicator = NaturalAreas__Percent().get_metric(zone)
    expected_zone_size = IDN_Jakarta_zone.zones.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size
    cleanup_cache_files(None, None, None, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_data_series_as_geojson(target_folder):
    zones = IDN_Jakarta_zone

    file_path = prep_output_path(target_folder, 'metric', 'data_series_csv.geojson')
    BuiltLandWithHighLST__Percent().write_as_geojson(zones, target_file_path=file_path)
    assert verify_file_is_populated(file_path)
    cleanup_cache_files(None, None, None, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_data_series_as_csv(target_folder):
    zones = IDN_Jakarta_zone

    file_path = prep_output_path(target_folder, 'metric', 'data_series_csv.csv')
    BuiltLandWithHighLST__Percent().write(zones, target_file_path=file_path)
    assert verify_file_is_populated(file_path)
    cleanup_cache_files(None, None, None, file_path)
