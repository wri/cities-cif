import ee
import pytest

from city_metrix.layers import NdviSentinel2, TreeCover, Albedo, AlosDSM
from tests.resources.bbox_constants import BBOX_BRA_LAURO_DE_FREITAS_1
from city_metrix.layers.layer import get_image_collection
from tests.tools.general_tools import post_process_layer

EE_IMAGE_DIMENSION_TOLERANCE = 1  # Tolerance compensates for variable results from GEE service
COUNTRY_CODE_FOR_BBOX = 'BRA'
BBOX = BBOX_BRA_LAURO_DE_FREITAS_1

def test_read_image_collection():
    ic = ee.ImageCollection("ESA/WorldCover/v100")
    data = get_image_collection(ic, BBOX, 10, "test")

    expected_crs = 32724
    expected_x_dimension = 187
    expected_y_dimension = 199

    assert data.rio.crs == expected_crs
    assert (
        pytest.approx(expected_x_dimension, rel=EE_IMAGE_DIMENSION_TOLERANCE) == "x",
        pytest.approx(expected_y_dimension, rel=EE_IMAGE_DIMENSION_TOLERANCE) == "y"
    )

def test_read_image_collection_scale():
    ic = ee.ImageCollection("ESA/WorldCover/v100")
    data = get_image_collection(ic, BBOX, 100, "test")
    expected_x_dimension = 19
    expected_y_dimension = 20
    assert data.dims == {"x": expected_x_dimension, "y": expected_y_dimension}

def test_albedo_dimensions():
    data = Albedo().get_data(BBOX)
    analysis_data = post_process_layer(data, value_threshold=0.1, convert_to_percentage=True)

    expected_min = 0
    expected_max = 34
    expected_peak_value = 15
    # peak_value, peak_count = get_count_by_value(analysis_data, expected_min, expected_max)

    # Bounding values
    actual_min = analysis_data.values.min()
    actual_max = analysis_data.values.max()

    # Peak frequency
    full_count = analysis_data.size
    mid_count_pct = get_value_percent(analysis_data, expected_peak_value, full_count, 0)

    # Value range
    assert actual_min == expected_min
    assert actual_max == expected_max
    # Peak frequency
    assert mid_count_pct == 21

def test_alos_dsm_dimensions():
    analysis_data = AlosDSM().get_data(BBOX)

    expected_min = 16
    expected_max = 86
    expected_peak_value = 56
    peak_value, peak_count = get_count_by_value(analysis_data, expected_min, expected_max)

    # Bounding values
    actual_min = analysis_data.values.min()
    actual_max = analysis_data.values.max()

    # Peak frequency
    full_count = analysis_data.size
    mid_count_pct = get_value_percent(analysis_data, expected_peak_value, full_count, 0)

    # Value range
    assert actual_min == expected_min
    assert actual_max == expected_max
    # Peak frequency
    assert mid_count_pct == 3
    
def test_ndvi_dimensions():
    data = NdviSentinel2(year=2023).get_data(BBOX)
    analysis_data = post_process_layer(data, value_threshold=0.4, convert_to_percentage=True)

    expected_min = 0
    expected_max = 85
    expected_peak_value = 78
    # peak_value, peak_count = get_count_by_value(analysis_data, expected_min, expected_max)

    # Bounding values
    actual_min = analysis_data.values.min()
    actual_max = analysis_data.values.max()

    # Peak frequency
    full_count = analysis_data.size
    mid_count_pct = get_value_percent(analysis_data, expected_peak_value, full_count, 0)

    # Value range
    assert actual_min == expected_min
    assert actual_max == expected_max
    # Peak frequency
    assert mid_count_pct == 11


def test_tree_cover():
    actual = TreeCover().get_data(BBOX).mean()
    expected = 54.0
    tolerance = 0.1
    assert (
            pytest.approx(expected, rel=tolerance) == actual
    )

def get_value_percent(data, value, full_count, precision):
    count_for_value = data.values[data.values == value].size
    percent_of_cells_with_value = get_rounded_pct(full_count, count_for_value, precision)
    return percent_of_cells_with_value

def get_rounded_pct(full_count, this_count, precision):
    return round((this_count/full_count)*100, precision)

def get_count_by_value(data, min_value, max_value):
    peak_value = None
    peak_count = 0
    for x in range(min_value, max_value):
        count = data.values[data.values == x].size
        if count > peak_count:
            peak_count = count
            peak_value = x

    return peak_value, peak_count