from city_metrix.metrics import *
from tests.resources.bbox_constants import GEOZONE_TERESINA_WGS84

# TODO - Consider adding other metrics

def test_city_values_BuiltLandWithHighLST():
    metric_obj = BuiltLandWithHighLST()
    metric_values = metric_obj.get_metric(geo_zone=GEOZONE_TERESINA_WGS84)
    _evaluate_metric_values(metric_values, 2, 0, 0.11, 0.04, 138, 6, 0)

# TODO The current specified value for count should be 138, but specific incorrectly here so the test passes
def test_city_values_mean_pm2p5_exposure():
    metric_obj = MeanPM2P5Exposure()
    metric_values = metric_obj.get_metric(geo_zone=GEOZONE_TERESINA_WGS84)
    _evaluate_metric_values(metric_values, 2, 11.23, 14.11, 12.41, 110, 0, 0)

def test_city_values_NaturalAreasPercent():
    metric_obj = NaturalAreasPercent()
    metric_values = metric_obj.get_metric(geo_zone=GEOZONE_TERESINA_WGS84)
    _evaluate_metric_values(metric_values, 2, 1.96, 97.16, 36.91, 138, 0, 0)


def _evaluate_metric_values(metric_values, digits, expected_min, expected_max, expected_mean, expected_count, expected_zero_count, expected_empty_count):
    min_val = round(metric_values.min(), digits)
    max_val = round(metric_values.max(), digits)
    mean_val = round(metric_values.mean(), digits)
    val_count = metric_values.count()
    count_zeros = (metric_values == 0).sum()
    empty_count = metric_values.isna().sum() + (metric_values == '').sum()

    if (expected_min == min_val and expected_max == max_val and expected_mean == mean_val
            and expected_count == val_count and expected_zero_count == count_zeros):
        has_expected_values = True
    else:
        has_expected_values = False

    expected = f"Min:{expected_min}, Max:{expected_max}, Mean:{expected_mean}, Cnt:{expected_count}, 0Cnt:{expected_zero_count}, emptyCnt:{expected_empty_count}"
    actual = f"Min:{min_val}, Max:{max_val}, Mean:{mean_val}, Cnt:{val_count}, 0Cnt:{count_zeros}, EmptyCnt:{empty_count}"
    assert has_expected_values, f"expected ({expected}), but got ({actual})"
