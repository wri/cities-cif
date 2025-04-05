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
polygon_coords = \
    [(-48.823576236608503, -27.431457531700953), (-48.666386558842795, -27.314448678159017),
     (-48.476834300360629, -27.373994958643205), (-48.467587848727355, -27.58112998150985),
     (-48.622465913584726, -27.68352771155466), (-48.735734946092371, -27.640532334533216),
     (-48.823576236608503, -27.431457531700953)]
BRA_Florianopolis_zone = (gpd
                          .GeoDataFrame([Polygon(polygon_coords)], columns=["geometry"])
                          .set_crs(WGS_CRS)
                          .reset_index())


@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason='Skipping since EXECUTE_IGNORED_TESTS set to False')
def test_write_natural_areas_polygonal(target_folder):
    zone = BRA_Florianopolis_zone
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'BRA_Florianopolis_natural_areas_polygon.geojson')

    NaturalAreasMetric().write(zone, file_path)
    assert verify_file_is_populated(file_path)
