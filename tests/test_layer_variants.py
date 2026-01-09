import ee
import numpy as np
import pytest

from city_metrix.constants import ProjectionType, WGS_CRS
from city_metrix.metrix_tools import get_projection_type
from city_metrix.metrix_model import get_image_collection, GeoExtent
from city_metrix.layers import AcagPM2p5, NdviSentinel2, TreeCover, Albedo, AlosDSM, Era5HottestDay, UtGlobus, \
    OvertureBuildingsHeight, AlbedoCloudMasked
from tests.resources.bbox_constants import BBOX_BRA_LAURO_DE_FREITAS_1, BBOX_USA_OR_PORTLAND_1, BBOX_IDN_JAKARTA
from tests.tools.spatial_tools import get_rounded_gdf_geometry
from tests.conftest import EXECUTE_IGNORED_TESTS
from tests.test_layers import assert_vector_stats, assert_raster_stats

# Tolerance compensates for variable results from GEE service
EE_IMAGE_DIMENSION_TOLERANCE = 1
COUNTRY_CODE_FOR_BBOX = 'BRA'
BBOX = BBOX_BRA_LAURO_DE_FREITAS_1

'''
Evalues various metrics of returned datasets, such as max value, min value, mean value, and 
array-dimension size.
'''

def test_read_image_collection():
    ic = ee.ImageCollection("ESA/WorldCover/v100")
    data = get_image_collection(ic, BBOX.to_ee_rectangle(), 10, "test")

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
    data = get_image_collection(ic, BBOX.to_ee_rectangle(), 100, "test")

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
    data = Albedo(start_date="2021-01-01", end_date="2022-01-01").get_data(BBOX, spatial_resolution=10)

    # Bounding values
    expected_min_value = _convert_fraction_to_rounded_percent(0.03)
    expected_max_value = _convert_fraction_to_rounded_percent(0.34)
    actual_min_value = _convert_fraction_to_rounded_percent(data.values.min())
    actual_max_value = _convert_fraction_to_rounded_percent(data.values.max())

    # Value range
    assert actual_min_value == expected_min_value
    assert actual_max_value == expected_max_value


def test_albedo_cloud_masked_southern_hemisphere():
    data = AlbedoCloudMasked().get_data(BBOX_IDN_JAKARTA)
    assert np.size(data) > 0
    assert_raster_stats(data, 2, 0.097, 1.0000, 1223220, 0)


def test_albedo_southern_hemisphere():
    data = Albedo().get_data(BBOX_IDN_JAKARTA)
    assert np.size(data) > 0
    assert_raster_stats(data, 2, 0.0057, 0.72, 1219518, 3702)


def test_albedo_metrics_no_resampling():
    data = Albedo(start_date="2021-01-01", end_date="2022-01-01").get_data(BBOX, spatial_resolution=10, resampling_method= None)

    # Bounding values
    expected_min_value = _convert_fraction_to_rounded_percent(0.03)
    expected_max_value = _convert_fraction_to_rounded_percent(0.34)
    actual_min_value = _convert_fraction_to_rounded_percent(data.values.min())
    actual_max_value = _convert_fraction_to_rounded_percent(data.values.max())

    # Value range
    assert actual_min_value == expected_min_value
    assert actual_max_value == expected_max_value


def test_albedo_metrics_default_date_range():
    data = Albedo().get_data(BBOX)

    # Representative values
    expected_median_value = _convert_fraction_to_rounded_percent(0.16326824)
    actual_median_value = _convert_fraction_to_rounded_percent(np.nanmedian(data.values[0]))

    # Value range
    assert actual_median_value == expected_median_value


def test_alos_dsm_values():
    data = AlosDSM().get_data(BBOX, resampling_method=None)

    # Bounding values
    expected_min_value = 16
    expected_max_value = 86
    actual_min_value = _convert_to_rounded_integer(data.values.min())
    actual_max_value = _convert_to_rounded_integer(data.values.max())

    # Value range
    assert actual_min_value == expected_min_value
    assert actual_max_value == expected_max_value


@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason="CDS API needs personal access token file to run")
def test_era_5_hottest_day_utc_30minute_offset():
    # Bhopal with timezone of UTC+5:30
    bbox = GeoExtent(bbox=(77.3886757, 23.2243898, 77.40987, 23.2427476), crs=WGS_CRS)
    data = Era5HottestDay(start_date="2023-01-01", end_date="2024-01-01", seasonal_utc_offset=5.5).get_data(bbox=bbox)

    assert data.time.values[0] == np.datetime64('2023-05-12T18')


def test_ndvi_values():
    data = NdviSentinel2(year=2023).get_data(BBOX)

    # Bounding values
    expected_min_value = _convert_fraction_to_rounded_percent(0.21)
    expected_max_value = _convert_fraction_to_rounded_percent(0.85)
    actual_min_value = _convert_fraction_to_rounded_percent(data.values.min())
    actual_max_value = _convert_fraction_to_rounded_percent(data.values.max())

    # Value range
    assert actual_min_value == expected_min_value
    assert actual_max_value == expected_max_value


def test_tree_cover_values():
    expected_mean_value = 54.0
    actual_mean_value = TreeCover().get_data(BBOX).mean()
    tolerance = 0.1
    assert (
        pytest.approx(expected_mean_value, rel=tolerance) == actual_mean_value
    )


def test_ut_globus_blank_city():
    data = UtGlobus().get_data(BBOX_USA_OR_PORTLAND_1)
    assert np.size(data) > 0
    assert_vector_stats(data, 'height', 0, 3, 16, 1095, 0)


def test_overture_height_rio():
    # tests an area with many overlapping buildings between UTGlobus and Overture
    city = 'rio_de_janerio'
    rio_bbox = GeoExtent(bbox=(-43.17135,-22.90901, -43.16832,-22.90598), crs=WGS_CRS)
    data = OvertureBuildingsHeight(city).get_data(rio_bbox)
    assert np.size(data) > 0
    assert_vector_stats(data, 'height', 1, 4.0, 436.0, 43, 0)


def test_wgs_utm_equivalency():
    BBOX = BBOX_USA_OR_PORTLAND_1
    BBOX_AS_UTM = BBOX.as_utm_bbox()

    data = AcagPM2p5().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_type(data.crs) == ProjectionType.UTM
    utm_bbox_data = AcagPM2p5().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))


def _convert_fraction_to_rounded_percent(fraction):
    return _convert_to_rounded_integer(fraction * 100)


def _convert_to_rounded_integer(value):
    return int(round(value))
