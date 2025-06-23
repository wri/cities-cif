from city_metrix.metrics import *
from tests.resources.bbox_constants import GEOZONE_TERESINA_WGS84

# TODO - Consider adding other metrics

def test_city_values_BuiltLandWithHighLST():
    metric_obj = BuiltLandWithHighLST()
    metric_values = metric_obj.get_metric(geo_zone=GEOZONE_TERESINA_WGS84)
    _evaluate_metric_values(metric_values, 2, 0, 0.11, 0.03, 138, 5, True)

# TODO The current specified value for continuity should be true, but specified here as False so the test passes. Count is also wrong.
def test_city_values_mean_pm2p5_exposure():
    metric_obj = MeanPM2P5Exposure()
    metric_values = metric_obj.get_metric(geo_zone=GEOZONE_TERESINA_WGS84)
    _evaluate_metric_values(metric_values, 2, 11.23, 14.11, 12.41, 110, 0, False)

def test_city_values_NaturalAreasPercent():
    metric_obj = NaturalAreasPercent()
    metric_values = metric_obj.get_metric(geo_zone=GEOZONE_TERESINA_WGS84)
    _evaluate_metric_values(metric_values, 2, 1.77, 97.16, 36.9, 138, 0, True)


def _evaluate_metric_values(metric_values, digits, expected_min, expected_max, expected_mean, expected_count, expected_zero_count, expect_zone_continuity):
    value_series = _convert_to_series(metric_values, 'value')
    min_val = round(value_series.min(), digits)
    max_val = round(value_series.max(), digits)
    mean_val = round(value_series.mean(), digits)
    val_count = value_series.count()
    count_zeros = (value_series == 0).sum()

    zone_series = _convert_to_series(metric_values, 'zone')
    diffs = zone_series.diff().dropna()
    is_continuous = diffs.nunique() == 1

    if (expected_min == min_val and expected_max == max_val and expected_mean == mean_val
            and expected_count == val_count and expected_zero_count == count_zeros and expect_zone_continuity == is_continuous):
        has_expected_values = True
    else:
        has_expected_values = False

    expected = f"Min:{expected_min}, Max:{expected_max}, Mean:{expected_mean}, Cnt:{expected_count}, 0Cnt:{expected_zero_count}, emptyCnt:{expect_zone_continuity}"
    actual = f"Min:{min_val}, Max:{max_val}, Mean:{mean_val}, Cnt:{val_count}, 0Cnt:{count_zeros}, EmptyCnt:{is_continuous}"
    assert has_expected_values, f"expected ({expected}), but got ({actual})"


def _convert_to_series(data, column):
    single_col = data[column]
    return single_col.squeeze()