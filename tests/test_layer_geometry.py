import math

import pytest

from city_metrix.layers.layer import WGS_CRS
from city_metrix.layers.layer_geometry import LayerBbox, create_fishnet_grid, _get_degree_offsets_for_meter_units, \
    get_haversine_distance
from tests.conftest import OR_PORTLAND_TILE

PORTLAND_LATLON_BBOX = LayerBbox(OR_PORTLAND_TILE.total_bounds, OR_PORTLAND_TILE.crs.srs)

def test_centroid_property():
    portland_centroid = OR_PORTLAND_TILE.centroid
    bbox_centroid = PORTLAND_LATLON_BBOX.centroid
    assert bbox_centroid.x == portland_centroid.x[0]

def test_roundtrip_projection():
    reproj_latlon_bbox = PORTLAND_LATLON_BBOX.as_utm_bbox().as_lat_lon_bbox()
    assert reproj_latlon_bbox.polygon.equals(PORTLAND_LATLON_BBOX.polygon)

def test_ee_rectangle1():
    utm_bbox = PORTLAND_LATLON_BBOX.as_utm_bbox()
    ll_ll_rectangle = PORTLAND_LATLON_BBOX.to_ee_rectangle("latlon")
    utm_ll_rectangle = utm_bbox.to_ee_rectangle("latlon")
    assert ll_ll_rectangle == utm_ll_rectangle

def test_ee_rectangle2():
    utm_bbox = PORTLAND_LATLON_BBOX.as_utm_bbox()
    ll_utm_rectangle = PORTLAND_LATLON_BBOX.to_ee_rectangle("utm")
    utm_utm_rectangle = utm_bbox.to_ee_rectangle("utm")
    assert ll_utm_rectangle == utm_utm_rectangle

def test_fishnet_in_degrees():
    bbox = LayerBbox(bbox=(10.0, 10, 11, 11), crs=WGS_CRS)
    tile_side_length = 0.5
    result_fishnet = (
        create_fishnet_grid(bbox, tile_side_length=tile_side_length, length_units="degrees",
                            output_as='latlon'))

    actual_count = result_fishnet.geometry.count()
    expected_count = 4
    assert actual_count == expected_count


def test_fishnet_in_meters():
    bbox = LayerBbox(bbox=(-38.0, -70.1, -37.9, -70.0), crs=WGS_CRS)
    tile_side_length = 1000
    buffer_size = 100
    result_fishnet = (
        create_fishnet_grid(bbox, tile_side_length=tile_side_length,
                            tile_buffer_size=buffer_size, length_units="meters"))

    actual_count = result_fishnet.geometry.count()
    expected_count = 48
    assert actual_count == expected_count

def test_extreme_large_side():
    bbox_crs = 'EPSG:4326'
    bbox = LayerBbox((100, 45, 100.5, 45.5), bbox_crs)

    with pytest.raises(ValueError, match='Value for tile_side_length is too large.'):
        create_fishnet_grid(bbox=bbox, tile_side_length=1, length_units='degrees', output_as='latlon')


def test_extreme_small_meters():
    bbox_crs = 'EPSG:4326'
    bbox = LayerBbox((100, 45, 101, 46), bbox_crs)

    with pytest.raises(ValueError, match='Value for tile_side_length is too small.'):
        create_fishnet_grid(bbox, tile_side_length=5, length_units='meters')

    with pytest.raises(ValueError, match='Failure. Grid would have too many cells along the x axis.'):
        create_fishnet_grid(bbox, tile_side_length=100, length_units='meters')


def test_degree_offsets_for_meter_units():
    ll_bbox = LayerBbox((45, 45, 46, 46), WGS_CRS)

    # values determined on https://www.omnicalculator.com/other/latitude-longitude-distance
    approx_x_offset = 78626
    approx_y_offset = 111195
    x_haversine = get_haversine_distance(45, 45, 46, 45)
    y_haversine = get_haversine_distance(45, 45, 45, 46)
    x_offset, y_offset = _get_degree_offsets_for_meter_units(ll_bbox, 1)

    tolerance = 0.2
    assert x_haversine == pytest.approx(approx_x_offset, abs=tolerance)
    assert y_haversine == pytest.approx(approx_y_offset, abs=tolerance)
    assert x_offset == pytest.approx(approx_x_offset, abs=tolerance)
    assert y_offset == pytest.approx(approx_y_offset, abs=tolerance)

