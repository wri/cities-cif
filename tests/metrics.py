from city_metrix import *
from .conftest import ZONES


def test_urban_open_space():
    indicator = urban_open_space(ZONES)
    assert indicator.size == 100


def test_built_land_with_low_surface_reflectivity():
    indicator = built_land_with_low_surface_reflectivity(ZONES)
    assert indicator.size == 100