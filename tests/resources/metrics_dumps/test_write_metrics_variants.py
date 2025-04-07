# This code is mostly intended for manual execution
# Execution configuration is specified in the conftest file
import os
import geopandas as gpd
import pytest

from city_metrix.constants import WGS_CRS
from city_metrix.metrics import *
from tests.resources.conftest import prep_output_path, verify_file_is_populated, EXECUTE_IGNORED_TESTS
from tests.tools.general_tools import create_target_folder

from shapely.geometry import Polygon
jakarta_crude_boundary = \
    [(106.688353778504393, -6.095658595454545),(106.971210221495596, -6.089509542346041),
     (106.972088657653956, -6.197557189824047),(106.907084381935476, -6.37412285765396),
     (106.796401425982395, -6.367973804545455),(106.690989086979457, -6.165055051964809),
     (106.688353778504393, -6.095658595454545)]

IDN_Jakarta_zone = (gpd.GeoDataFrame([Polygon(jakarta_crude_boundary)], columns=["geometry"])
                    .set_crs(WGS_CRS)
                    .reset_index())


@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_polygonal_zones(target_folder):
    zone = IDN_Jakarta_zone
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'IDN_Jakarta_natural_areas_polygon.geojson')

    NaturalAreasPercent().write(zone, file_path)
    assert verify_file_is_populated(file_path)

    indicator = NaturalAreasPercent().get_data(zone)
    expected_zone_size = IDN_Jakarta_zone.geometry.size
    actual_indicator_size = indicator.size
    assert expected_zone_size == actual_indicator_size

