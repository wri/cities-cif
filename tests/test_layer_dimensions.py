from city_metrix.layers import NdviSentinel2
from tests.resources.bbox_constants import BBOX_BRA_LAURO_DE_FREITAS_1
from tests.tools import post_process_layer

COUNTRY_CODE_FOR_BBOX = 'BRA'
BBOX = BBOX_BRA_LAURO_DE_FREITAS_1

def test_ndvi_dimensions():
    data = NdviSentinel2(year=2023).get_data(BBOX)
    data_for_map = post_process_layer(data, value_threshold=0.4, convert_to_percentage=True)

    expected_size = 37213
    actual_size = data_for_map.size
    expected_min = 0
    actual_min = data_for_map.values.min()
    expected_max = 85
    actual_max = data_for_map.values.max()

    assert actual_size == expected_size
    assert actual_min == expected_min
    assert actual_max == expected_max
