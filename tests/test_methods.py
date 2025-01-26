import math

import numpy as np
import pytest
from city_metrix.layers.layer import create_fishnet_grid, WGS_CRS
from city_metrix.layers.layer_geometry import LayerBbox
from .conftest import (
    LARGE_IDN_JAKARTA_TILED_ZONES,
    IDN_JAKARTA_TILED_ZONES,
    MockGroupByLayer,
    MockLargeGroupByLayer,
    MockLargeLayer,
    MockLayer,
    MockMaskLayer,
)

def test_count():
    counts = MockLayer().groupby(IDN_JAKARTA_TILED_ZONES).count()
    assert counts.size == 100
    assert all([count == 100 for count in counts])

def test_mean():
    means = MockLayer().groupby(IDN_JAKARTA_TILED_ZONES).mean()
    assert means.size == 100
    assert all([mean == i for i, mean in enumerate(means)])


def test_fishnetted_count():
    counts = MockLargeLayer().groupby(LARGE_IDN_JAKARTA_TILED_ZONES).count()
    assert counts.size == 100
    assert all([count == 100 for count in counts])


def test_fishnetted_mean():
    means = MockLargeLayer().groupby(LARGE_IDN_JAKARTA_TILED_ZONES).mean()
    assert means.size == 100
    assert all([mean == i for i, mean in enumerate(means)])

def test_fishnet_in_meters():
    min_x = -38.3
    min_y = -70.1
    max_x = -38.2
    max_y = -70.0
    bbox = LayerBbox(bbox=(min_x, min_y, max_x, max_y), crs=WGS_CRS)
    tile_side_length = 1000
    buffer_size = 100
    result_fishnet = (
        create_fishnet_grid(bbox, tile_side_length=tile_side_length,
                            tile_buffer_size=buffer_size, length_units="meters"))

    actual_count = result_fishnet.geometry.count()
    expected_count = 48
    assert actual_count == expected_count


def test_meters_to_offset_degrees():
    decimal_latitude = 45
    length_m = 100
    lon_degree_offset, lat_degree_offset = offset_meters_to_geographic_degrees(decimal_latitude, length_m)

    assert round(lon_degree_offset,5) == 0.00127
    assert round(lat_degree_offset,5) == 0.0009


def test_masks():
    counts = MockLayer().mask(MockMaskLayer()).groupby(IDN_JAKARTA_TILED_ZONES).count()
    assert counts.size == 100
    for i, count in enumerate(counts):
        if i % 2 == 0:
            assert np.isnan(count)
        else:
            assert count == 100


def test_group_by_layer():
    counts = MockLayer().groupby(IDN_JAKARTA_TILED_ZONES, layer=MockGroupByLayer()).count()
    assert all([count == {1: 50.0, 2: 50.0} for count in counts])


def test_group_by_large_layer():
    counts = (
        MockLargeLayer().groupby(LARGE_IDN_JAKARTA_TILED_ZONES, layer=MockLargeGroupByLayer()).count()
    )
    assert all([count == {1: 50.0, 2: 50.0} for count in counts])

def test_extreme_large_side():
    min_x = 100
    min_y = 45
    max_x = 101
    max_y = 46
    bbox_crs = 'EPSG:4326'
    tile_side_length = 1
    bbox = LayerBbox((min_x, min_y, max_x, max_y), bbox_crs)

    with pytest.raises(ValueError):
        create_fishnet_grid(bbox=bbox, tile_side_length=tile_side_length, length_units='degrees', output_as='latlon')

def test_extreme_small_meters():
    min_x = 100
    min_y = 45
    max_x = 100.5
    max_y = 45.5
    bbox_crs = 'EPSG:4326'
    tile_side_length= 10

    with pytest.raises(Exception) as e_info:
        create_fishnet_grid(min_x, min_y, max_x, max_y, bbox_crs=bbox_crs,
                            tile_side_length=tile_side_length, length_units='meters')


def offset_meters_to_geographic_degrees(decimal_latitude, length_m):
    # TODO consider replacing this spherical calculation with ellipsoidal
    earth_radius_m = 6378137
    rad = 180/math.pi

    lon_degree_offset = abs((length_m / (earth_radius_m * math.cos(math.pi*decimal_latitude/180))) * rad)
    lat_degree_offset = abs((length_m / earth_radius_m) * rad)

    return lon_degree_offset, lat_degree_offset
