from city_metrix.metrics import *
from tests.resources.bbox_constants import GEOZONE_TERESINA_WGS84

# TODO - Consider adding other metrics

def test_write_BuiltLandWithHighLST():
    metric_obj = BuiltLandWithHighLST()
    metric_values = metric_obj.get_metric(geo_zone=GEOZONE_TERESINA_WGS84)
    _evaluate_metric_values(metric_values, 2, 0, 0.11, 0.04, 138)


def test_write_NaturalAreasPercent():
    metric_obj = NaturalAreasPercent()
    metric_values = metric_obj.get_metric(geo_zone=GEOZONE_TERESINA_WGS84)
    _evaluate_metric_values(metric_values, 2, 1.96, 97.16, 36.91, 138)


def _evaluate_metric_values(metric_values, digits, expected_min, expected_max, expected_mean, expected_count):
    min_val = round(metric_values.min(), digits)
    max_val = round(metric_values.max(), digits)
    mean_val = round(metric_values.mean(), digits)
    val_count = metric_values.count()

    if expected_min == min_val and expected_max == max_val and expected_mean == mean_val and expected_count == val_count:
        has_expected_values = True
    else:
        has_expected_values = False

    if has_expected_values is False:
        print(f"min_max_mean_count - Expected: {expected_min}, {expected_max}, {expected_mean}, {expected_count} Actual: {min_val}, {max_val}, {mean_val}, {val_count}")

    assert has_expected_values
