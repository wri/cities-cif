import ee
import pytest

from city_metrix.layers import NdviSentinel2, TreeCover, Albedo, AlosDSM
from tests.resources.bbox_constants import BBOX_BRA_LAURO_DE_FREITAS_1
from city_metrix.layers.layer import get_image_collection

EE_IMAGE_DIMENSION_TOLERANCE = 1  # Tolerance compensates for variable results from GEE service
COUNTRY_CODE_FOR_BBOX = 'BRA'
BBOX = BBOX_BRA_LAURO_DE_FREITAS_1

'''
Evalues various metrics of returned datasets, such as max value, min value, mean value, and 
array-dimension size.
'''

def test_read_image_collection():
    ic = ee.ImageCollection("ESA/WorldCover/v100")
    data = get_image_collection(ic, BBOX, 10, "test")

    expected_crs = 32724
    expected_x_size = 186
    expected_y_size = 199
    
    actual_crs = data.rio.crs
    actual_x_size = data['x'].size
    actual_y_size = data['y'].size

    assert expected_crs == actual_crs
    assert (
        pytest.approx(expected_x_size, rel=EE_IMAGE_DIMENSION_TOLERANCE) == actual_x_size,
        pytest.approx(expected_y_size, rel=EE_IMAGE_DIMENSION_TOLERANCE) == actual_y_size
    )

def test_read_image_collection_scale():
    ic = ee.ImageCollection("ESA/WorldCover/v100")
    data = get_image_collection(ic, BBOX, 100, "test")

    expected_x_size = 19
    expected_y_size = 20

    actual_x_size = data['x'].size
    actual_y_size = data['y'].size

    assert (
        pytest.approx(expected_x_size, rel=EE_IMAGE_DIMENSION_TOLERANCE) == actual_x_size,
        pytest.approx(expected_y_size, rel=EE_IMAGE_DIMENSION_TOLERANCE) == actual_y_size
    )

def test_albedo_metrics_default_resampling():
    # Default resampling_method is bilinear
    data = Albedo(spatial_resolution=10).get_data(BBOX)

    # Bounding values
    expected_min_value = _convert_fraction_to_rounded_percent(0.03)
    expected_max_value = _convert_fraction_to_rounded_percent(0.34)
    actual_min_value = _convert_fraction_to_rounded_percent(data.values.min())
    actual_max_value = _convert_fraction_to_rounded_percent(data.values.max())

    # Value range
    assert expected_min_value == actual_min_value
    assert expected_max_value == actual_max_value


def test_albedo_metrics_no_resampling():
    data = Albedo(spatial_resolution=10, resampling_method= None).get_data(BBOX)

    # Bounding values
    expected_min_value = _convert_fraction_to_rounded_percent(0.03)
    expected_max_value = _convert_fraction_to_rounded_percent(0.34)
    actual_min_value = _convert_fraction_to_rounded_percent(data.values.min())
    actual_max_value = _convert_fraction_to_rounded_percent(data.values.max())

    # Value range
    assert expected_min_value == actual_min_value
    assert expected_max_value == actual_max_value


def test_alos_dsm_metrics():
    data = AlosDSM(resampling_method=None).get_data(BBOX)

    # Bounding values
    expected_min_value = 16
    expected_max_value = 86
    actual_min_value = _convert_to_rounded_integer(data.values.min())
    actual_max_value = _convert_to_rounded_integer(data.values.max())

    # Value range
    assert expected_min_value == actual_min_value
    assert expected_max_value == actual_max_value

    
def test_ndvi_metrics():
    data = NdviSentinel2(year=2023).get_data(BBOX)

    # Bounding values
    expected_min_value = _convert_fraction_to_rounded_percent(0.21)
    expected_max_value = _convert_fraction_to_rounded_percent(0.85)
    actual_min_value = _convert_fraction_to_rounded_percent(data.values.min())
    actual_max_value = _convert_fraction_to_rounded_percent(data.values.max())

    # Value range
    assert actual_min_value == expected_min_value
    assert actual_max_value == expected_max_value


def test_tree_cover_metrics():
    expected_mean_value = 54.0
    actual_mean_value = TreeCover().get_data(BBOX).mean()
    tolerance = 0.1
    assert (
            pytest.approx(expected_mean_value, rel=tolerance) == actual_mean_value
    )

def _convert_fraction_to_rounded_percent(fraction):
        return _convert_to_rounded_integer(fraction * 100)


def _convert_to_rounded_integer(value):
    return int(round((value)))

