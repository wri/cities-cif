import math

import numpy as np
import pytest

from city_metrix.constants import ProjectionType
from city_metrix.layers import NasaDEM
from city_metrix.layers.layer import WGS_CRS
from city_metrix.layers.layer_geometry import GeoExtent, create_fishnet_grid, _get_degree_offsets_for_meter_units, \
    get_haversine_distance
from tests.conftest import USA_OR_PORTLAND_BBOX
from tests.resources.bbox_constants import GEOEXTENT_SMALL_CITY_WGS84, GEOEXTENT_SMALL_CITY_UTM
from tests.tools.spatial_tools import get_rounded_geometry

USA_OR_PORTLAND_LATLON_BBOX = GeoExtent(USA_OR_PORTLAND_BBOX.total_bounds, USA_OR_PORTLAND_BBOX.crs.srs)

def test_city_extent():
    city_geo_extent = GEOEXTENT_SMALL_CITY_WGS84
    geom = city_geo_extent.centroid
    rounded_boundary_centroid = get_rounded_geometry(geom, 1)
    assert city_geo_extent.projection_type == ProjectionType.GEOGRAPHIC
    assert rounded_boundary_centroid == 'POINT (-42.8 -5.1)'

def test_nasa_dem_city_id_wgs84():
    data = NasaDEM().get_data(GEOEXTENT_SMALL_CITY_WGS84)
    assert np.size(data) > 0

def test_nasa_dem_city_id_utm():
    data = NasaDEM().get_data(GEOEXTENT_SMALL_CITY_UTM)
    assert np.size(data) > 0

def test_centroid_property():
    portland_centroid = USA_OR_PORTLAND_BBOX.centroid
    bbox_centroid = USA_OR_PORTLAND_LATLON_BBOX.centroid
    assert bbox_centroid.x == portland_centroid.x[0]

def test_roundtrip_projection():
    reproj_latlon_bbox = USA_OR_PORTLAND_LATLON_BBOX.as_utm_bbox().as_geographic_bbox()
    assert reproj_latlon_bbox.to_ee_rectangle()['bounds'] == USA_OR_PORTLAND_LATLON_BBOX.to_ee_rectangle()['bounds']
    assert reproj_latlon_bbox.crs == USA_OR_PORTLAND_LATLON_BBOX.crs

def test_ee_rectangle1():
    utm_ll_rectangle = USA_OR_PORTLAND_LATLON_BBOX.as_utm_bbox().to_ee_rectangle()
    ll_ll_rectangle = USA_OR_PORTLAND_LATLON_BBOX.to_ee_rectangle()
    assert ll_ll_rectangle == utm_ll_rectangle


def test_fishnet_in_degrees():
    bbox = GeoExtent(bbox=(10.0, 10, 11, 11), crs=WGS_CRS)
    tile_side_length = 0.5
    result_fishnet = (
        create_fishnet_grid(bbox, tile_side_length=tile_side_length, length_units="degrees",
                            output_as=ProjectionType.GEOGRAPHIC))

    actual_count = result_fishnet.geometry.count()
    expected_count = 4
    assert actual_count == expected_count


def test_fishnet_in_meters():
    bbox = GeoExtent(bbox=(-38.0, -70.1, -37.9, -70.0), crs=WGS_CRS)
    tile_side_length = 1000
    buffer_size = 100
    result_fishnet = (
        create_fishnet_grid(bbox, tile_side_length=tile_side_length,
                            tile_buffer_size=buffer_size, length_units="meters"))

    actual_count = result_fishnet.geometry.count()
    expected_count = 48
    assert actual_count == expected_count

def test_extreme_large_side():
    bbox_crs = WGS_CRS
    bbox = GeoExtent((100, 45, 100.5, 45.5), bbox_crs)

    with pytest.raises(ValueError, match='Value for tile_side_length is too large.'):
        create_fishnet_grid(bbox=bbox, tile_side_length=1, length_units='degrees', output_as=ProjectionType.GEOGRAPHIC)


def test_extreme_small_meters():
    bbox_crs = WGS_CRS
    bbox = GeoExtent((100, 45, 101, 46), bbox_crs)

    with pytest.raises(ValueError, match='Failure. Grid would have too many cells along the x axis.'):
        create_fishnet_grid(bbox, tile_side_length=100, length_units='meters')


def test_degree_offsets_for_meter_units():
    ll_bbox = GeoExtent((45, 45, 46, 46), WGS_CRS)

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

