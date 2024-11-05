import numpy as np
import pytest
from city_metrix.layers.layer import create_fishnet_grid, offset_meters_to_geographic_degrees
from .conftest import (
    LARGE_ZONES,
    ZONES,
    MockGroupByLayer,
    MockLargeGroupByLayer,
    MockLargeLayer,
    MockLayer,
    MockMaskLayer,
)

def test_count():
    counts = MockLayer().groupby(ZONES).count()
    assert counts.size == 100
    assert all([count == 100 for count in counts])

def test_mean():
    means = MockLayer().groupby(ZONES).mean()
    assert means.size == 100
    assert all([mean == i for i, mean in enumerate(means)])


def test_fishnetted_count():
    counts = MockLargeLayer().groupby(LARGE_ZONES).count()
    assert counts.size == 100
    assert all([count == 100 for count in counts])


def test_fishnetted_mean():
    means = MockLargeLayer().groupby(LARGE_ZONES).mean()
    assert means.size == 100
    assert all([mean == i for i, mean in enumerate(means)])

def test_fishnet_in_meters():
    min_x = -38.3
    min_y = -80.1
    max_x = -38.2
    max_y = -80.0
    tile_side_meters = 1000
    tile_buffer_meters = 100
    result_fishnet = (
        create_fishnet_grid(min_x, min_y, max_x, max_y, tile_side_meters, tile_buffer_meters, tile_units_in_degrees=False))

    actual_count = result_fishnet.geometry.count()
    expected_count = 24
    assert actual_count == expected_count


def test_meters_to_offset_degrees():
    decimal_latitude = 45
    length_m = 100
    lon_degree_offset, lat_degree_offset = offset_meters_to_geographic_degrees(decimal_latitude, length_m)

    assert round(lon_degree_offset,5) == 0.00127
    assert round(lat_degree_offset,5) == 0.0009


def test_masks():
    counts = MockLayer().mask(MockMaskLayer()).groupby(ZONES).count()
    assert counts.size == 100
    for i, count in enumerate(counts):
        if i % 2 == 0:
            assert np.isnan(count)
        else:
            assert count == 100


def test_group_by_layer():
    counts = MockLayer().groupby(ZONES, layer=MockGroupByLayer()).count()
    assert all([count == {1: 50.0, 2: 50.0} for count in counts])


def test_group_by_large_layer():
    counts = (
        MockLargeLayer().groupby(LARGE_ZONES, layer=MockLargeGroupByLayer()).count()
    )
    assert all([count == {1: 50.0, 2: 50.0} for count in counts])

def test_extreme_large_degrees():
    min_x = 100
    min_y = 45
    max_x = 100.5
    max_y = 45.5
    cell_size_degrees = 1

    with pytest.raises(Exception):
        create_fishnet_grid(min_x, min_y, max_x, max_y, cell_size_degrees)

def test_extreme_small_meters():
    min_x = 100
    min_y = 45
    max_x = 100.5
    max_y = 45.5
    cell_size_meters= 1

    with pytest.raises(Exception) as e_info:
        create_fishnet_grid(min_x, min_y, max_x, max_y, cell_size_meters, tile_units_in_degrees=False)
