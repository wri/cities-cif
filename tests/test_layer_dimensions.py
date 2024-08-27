import numpy as np

from city_metrix.layers import NdviSentinel2
from tests.resources.bbox_constants import BBOX_BRA_LAURO_DE_FREITAS_1
from tests.tools import post_process_layer

COUNTRY_CODE_FOR_BBOX = 'BRA'
BBOX = BBOX_BRA_LAURO_DE_FREITAS_1

def test_ndvi_dimensions():
    data = NdviSentinel2(year=2023).get_data(BBOX)
    thinned_data = post_process_layer(data, value_threshold=0.4, convert_to_percentage=True)

    expected_min = 0
    actual_min = thinned_data.values.min()
    expected_max = 85
    actual_max = thinned_data.values.max()

    # Bounding distribution of values
    full_count = thinned_data.size
    min_count = thinned_data.values[thinned_data.values == expected_min].size
    min_count_pct = get_rounded_pct(full_count, min_count, 1)
    max_count = thinned_data.values[thinned_data.values == expected_max].size
    max_count_pct = get_rounded_pct(full_count, max_count, 1)

    mid_range_value = round((expected_min+expected_max)/2)
    mid_count = thinned_data.values[thinned_data.values == mid_range_value].size
    mid_count_pct = get_rounded_pct(full_count, mid_count, 1)

    # Value range
    assert actual_min == 0
    assert actual_max == 85
    # Value distribution
    assert min_count_pct == 6.7
    assert max_count_pct == 0
    assert mid_count_pct == 0.3


def get_rounded_pct(full_count, this_count, precision):
    return round((this_count/full_count)*100, precision)
