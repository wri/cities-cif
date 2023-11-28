from city_metrix import *
from .conftest import ZONES


def test_urban_open_space():
    indicator = urban_open_space(ZONES)
    assert indicator.size == 100
