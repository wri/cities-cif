import pytest
import numpy as np
from skimage.metrics import structural_similarity as ssim
from pyproj import CRS
from xarray.core.ops import fillna
from xrspatial import quantile

from city_metrix.layers import (
    Layer,
    Albedo,
    AlosDSM,
    AverageNetBuildingHeight,
    BuiltUpHeight,
    EsaWorldCover, EsaWorldCoverClass,
    LandSurfaceTemperature,
    NasaDEM,
    NaturalAreas,
    NdviSentinel2,
    TreeCanopyHeight,
    TreeCover,
    UrbanLandUse,
    WorldPop, OpenStreetMap, HighLandSurfaceTemperature
)
from tests.resources.bbox_constants import BBOX_BRA_LAURO_DE_FREITAS_1
from tests.tools.general_tools import get_class_from_instance, get_class_default_spatial_resolution

"""
Evaluation of spatial_resolution property 
To add a test for a scalable layer that has the spatial_resolution property:
1. Add the class name to the city_metrix.layers import statement above
2. Copy an existing test_*_spatial_resolution() test
   a. rename for the new layer
   b. specify a minimal class instance for the layer, not specifying the spatial_resolution attribute.
"""

COUNTRY_CODE_FOR_BBOX = 'BRA'
BBOX = BBOX_BRA_LAURO_DE_FREITAS_1
RESOLUTION_COMPARISON_TOLERANCE = 1
DOWNSIZE_FACTOR = 2

def test_albedo_downsampled_spatial_resolution():
    class_instance = Albedo()
    default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = get_sample_data(class_instance)
    downsizing_is_within_tolerances = evaluate_raster_value(default_res_data, downsized_res_data)

    assert pytest.approx(target_downsized_res, rel=RESOLUTION_COMPARISON_TOLERANCE) == estimated_actual_res
    assert downsizing_is_within_tolerances

def test_alos_dsm_downsampled_spatial_resolution():
    class_instance = AlosDSM()
    default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = get_sample_data(class_instance)
    downsizing_is_within_tolerances = evaluate_raster_value(default_res_data, downsized_res_data)

    assert pytest.approx(target_downsized_res, rel=RESOLUTION_COMPARISON_TOLERANCE) == estimated_actual_res
    assert downsizing_is_within_tolerances

def test_average_net_building_height_downsampled_spatial_resolution():
    class_instance = AverageNetBuildingHeight()
    default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = get_sample_data(class_instance)
    downsizing_is_within_tolerances = evaluate_raster_value(default_res_data, downsized_res_data)

    assert pytest.approx(target_downsized_res, rel=RESOLUTION_COMPARISON_TOLERANCE) == estimated_actual_res
    assert downsizing_is_within_tolerances

def test_built_up_height_downsampled_spatial_resolution():
    class_instance = BuiltUpHeight()
    default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = get_sample_data(class_instance)
    downsizing_is_within_tolerances = evaluate_raster_value(default_res_data, downsized_res_data)

    assert pytest.approx(target_downsized_res, rel=RESOLUTION_COMPARISON_TOLERANCE) == estimated_actual_res
    assert downsizing_is_within_tolerances

def test_esa_world_cover_downsampled_spatial_resolution():
    class_instance = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
    default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = get_sample_data(class_instance)
    downsizing_is_within_tolerances = evaluate_raster_value(default_res_data, downsized_res_data)

    assert pytest.approx(target_downsized_res, rel=RESOLUTION_COMPARISON_TOLERANCE) == estimated_actual_res
    assert downsizing_is_within_tolerances

def test_high_land_surface_temperature_downsampled_spatial_resolution():
    class_instance = HighLandSurfaceTemperature()
    default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = get_sample_data(class_instance)
    downsizing_is_within_tolerances = evaluate_raster_value(default_res_data, downsized_res_data)

    assert pytest.approx(target_downsized_res, rel=RESOLUTION_COMPARISON_TOLERANCE) == estimated_actual_res
    assert downsizing_is_within_tolerances

def test_land_surface_temperature_downsampled_spatial_resolution():
    class_instance = LandSurfaceTemperature()
    default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = get_sample_data(class_instance)
    downsizing_is_within_tolerances = evaluate_raster_value(default_res_data, downsized_res_data)

    assert pytest.approx(target_downsized_res, rel=RESOLUTION_COMPARISON_TOLERANCE) == estimated_actual_res
    assert downsizing_is_within_tolerances

def test_nasa_dem_downsampled_spatial_resolution():
    class_instance = NasaDEM()
    default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = get_sample_data(class_instance)
    downsizing_is_within_tolerances = evaluate_raster_value(default_res_data, downsized_res_data)

    assert pytest.approx(target_downsized_res, rel=RESOLUTION_COMPARISON_TOLERANCE) == estimated_actual_res
    assert downsizing_is_within_tolerances

def test_natural_areas_downsampled_spatial_resolution():
    class_instance = NaturalAreas()
    default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = get_sample_data(class_instance)
    downsizing_is_within_tolerances = evaluate_raster_value(default_res_data, downsized_res_data)

    assert pytest.approx(target_downsized_res, rel=RESOLUTION_COMPARISON_TOLERANCE) == estimated_actual_res
    assert downsizing_is_within_tolerances

def test_ndvi_sentinel2_downsampled_spatial_resolution():
    class_instance = NdviSentinel2(year=2023)
    default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = get_sample_data(class_instance)
    downsizing_is_within_tolerances = evaluate_raster_value(default_res_data, downsized_res_data)

    assert pytest.approx(target_downsized_res, rel=RESOLUTION_COMPARISON_TOLERANCE) == estimated_actual_res
    assert downsizing_is_within_tolerances

def test_tree_canopy_height_downsampled_spatial_resolution():
    class_instance = TreeCanopyHeight()
    default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = get_sample_data(class_instance)
    downsizing_is_within_tolerances = evaluate_raster_value(default_res_data, downsized_res_data)

    assert pytest.approx(target_downsized_res, rel=RESOLUTION_COMPARISON_TOLERANCE) == estimated_actual_res
    assert downsizing_is_within_tolerances

def test_tree_cover_downsampled_spatial_resolution():
    class_instance = TreeCover()
    default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = get_sample_data(class_instance)
    downsizing_is_within_tolerances = evaluate_raster_value(default_res_data, downsized_res_data)

    assert pytest.approx(target_downsized_res, rel=RESOLUTION_COMPARISON_TOLERANCE) == estimated_actual_res
    assert downsizing_is_within_tolerances

def test_urban_land_use_downsampled_spatial_resolution():
    class_instance = UrbanLandUse()
    default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = get_sample_data(class_instance)
    downsizing_is_within_tolerances = evaluate_raster_value(default_res_data, downsized_res_data)

    assert pytest.approx(target_downsized_res, rel=RESOLUTION_COMPARISON_TOLERANCE) == estimated_actual_res
    assert downsizing_is_within_tolerances

def test_world_pop_downsampled_spatial_resolution():
    class_instance = WorldPop()
    default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = get_sample_data(class_instance)
    downsizing_is_within_tolerances = evaluate_raster_value(default_res_data, downsized_res_data)

    assert pytest.approx(target_downsized_res, rel=RESOLUTION_COMPARISON_TOLERANCE) == estimated_actual_res
    assert downsizing_is_within_tolerances

def test_halved_up_sampled_spatial_resolution():
    class_instance = Albedo()
    halved_default_resolution = get_class_default_spatial_resolution(class_instance) / 2

    expected_resolution = halved_default_resolution
    modified_data = get_modified_resolution_data(class_instance, halved_default_resolution)
    estimated_actual_resolution = estimate_spatial_resolution(modified_data)

    assert expected_resolution == estimated_actual_resolution

def test_null_spatial_resolution():
    class_instance = Albedo()
    spatial_resolution=None

    with pytest.raises(Exception) as e_info:
        get_modified_resolution_data(class_instance, spatial_resolution)

def test_function_validate_layer_instance():
    is_valid, except_str = validate_layer_instance('t')
    assert is_valid is False
    is_valid, except_str = validate_layer_instance(EsaWorldCoverClass.BUILT_UP)
    assert is_valid is False
    is_valid, except_str = validate_layer_instance(OpenStreetMap())
    assert is_valid is False
    is_valid, except_str = validate_layer_instance(Albedo(spatial_resolution = 2))
    assert is_valid is False

def get_sample_data(class_instance):
    is_valid, except_str = validate_layer_instance(class_instance)
    if is_valid is False:
        raise Exception(except_str)

    default_res = get_class_default_spatial_resolution(class_instance)
    downsized_resolution = DOWNSIZE_FACTOR * default_res

    downsized_res_data = get_modified_resolution_data(class_instance, downsized_resolution)
    default_res_data = get_modified_resolution_data(class_instance, default_res)

    estimated_actual_resolution = estimate_spatial_resolution(downsized_res_data)

    return default_res_data, downsized_res_data, downsized_resolution, estimated_actual_resolution

def get_crs_from_image_data(image_data):
    crs_string = image_data.rio.crs.data['init']
    crs = CRS.from_string(crs_string)
    return crs


def get_modified_resolution_data(class_instance, spatial_resolution):
    class_instance.spatial_resolution = spatial_resolution
    data = class_instance.get_data(BBOX)
    return data

def validate_layer_instance(obj):
    is_valid = True
    except_str = None

    if not obj.__class__.__bases__[0] == Layer:
        is_valid = False
        except_str = "Specified object '%s' is not a valid Layer class instance." % obj
    else:
        cls = get_class_from_instance(obj)
        cls_name = type(cls).__name__
        if not hasattr(obj, 'spatial_resolution'):
            is_valid = False
            except_str = "Class '%s' does not have spatial_resolution property." % cls_name
        elif not obj.spatial_resolution == cls.spatial_resolution:
            is_valid = False
            except_str = "Do not specify spatial_resolution property value for class '%s'." % cls_name
        elif cls.spatial_resolution is None:
            is_valid = False
            except_str = "Signature of class %s must specify a non-null default value for spatial_resolution. Please correct." % cls_name

    return is_valid, except_str

def estimate_spatial_resolution(data):
    y_cells = float(data['y'].size - 1)
    y_min = data.coords['y'].values.min()
    y_max = data.coords['y'].values.max()

    crs = get_crs_from_image_data(data)
    crs_unit = crs.axis_info[0].unit_name

    if crs_unit == 'metre':
        diff_distance = y_max - y_min
    else:
        raise Exception('Unhandled projection units: %s for projection: %s' % (crs_unit, crs.srs))

    estimated_actual_resolution = round(diff_distance / y_cells)

    return estimated_actual_resolution

def get_populate_ratio(dataset):
    raw_data_size = dataset.values.size
    populated_raw_data = dataset.values[(~np.isnan(dataset.values)) & (dataset.values > 0)]
    populated_data_raw_size = populated_raw_data.size
    populated_raw_data_ratio = populated_data_raw_size/raw_data_size
    return populated_raw_data_ratio

def fill_ndarray(data):
    # Note offset avoids situation where dataset has only one value besides nan
    min_vals = data[~np.isnan(data)].mean()-.01
    filled_data = np.nan_to_num(data, copy=True, nan=min_vals, posinf=None, neginf=None)
    return filled_data

def get_normalized_quantile(ndarray, q):
    normalized_data = (ndarray - ndarray.min()) / (ndarray.max() - ndarray.min())
    normalized_quantile = np.quantile(normalized_data, q)
    return round(normalized_quantile, 2)

def get_normalized_stdev(ndarray):
    mean = abs(np.mean(ndarray))
    std_dev = np.std(ndarray)
    normalized_std_dev = std_dev / mean
    return round(normalized_std_dev, 2)

def evaluate_raster_value(raw_data, downsized_data):
    # Below tolerances where determined through trial and error evaluation of results in QGIS

    populated_raw_data_ratio = get_populate_ratio(raw_data)
    populated_downsized_data_ratio = get_populate_ratio(downsized_data)
    ratio_diff = abs(populated_raw_data_ratio - populated_downsized_data_ratio)
    ratio_eval = True if ratio_diff <= 0.2 else False

    # Fill nan values so that all cells are included in stats
    filled_raw_data = fill_ndarray(raw_data.values)
    filled_downsized_data = fill_ndarray(downsized_data.values)

    if (((filled_raw_data.max() - filled_raw_data.min()) == 0) or
            ((filled_downsized_data.max() - filled_downsized_data.min()) ==0)):
        nq_evals = False
        stnaratio_eval = False

    else:
        # Examine the general distribution of the data using 0.25, .50, and 0.75 quantiles
        nq25_raw_data = get_normalized_quantile(filled_raw_data, 0.25)
        nq50_raw_data = get_normalized_quantile(filled_raw_data, 0.5)
        nq75_raw_data = get_normalized_quantile(filled_raw_data, 0.75)
        nq25_downsized_data = get_normalized_quantile(filled_downsized_data, 0.25)
        nq50_downsized_data = get_normalized_quantile(filled_downsized_data, 0.5)
        nq75_downsized_data = get_normalized_quantile(filled_downsized_data, 0.75)

        # Hacky adjustment of tolerance for coarse rasterization
        nq_tolerance = 0.1 if filled_downsized_data.size > 100 else 0.2
        nq25_eval = True if abs(nq25_raw_data - nq25_downsized_data) <= nq_tolerance else False
        nq50_eval = True if abs(nq50_raw_data - nq50_downsized_data) <= nq_tolerance else False
        nq75_eval = True if abs(nq75_raw_data - nq75_downsized_data) <= nq_tolerance else False
        nq_evals = True if (nq25_eval & nq50_eval & nq75_eval) else False

        nstdev_raw_data = get_normalized_stdev(filled_raw_data)
        nstdev_downsized_data = get_normalized_stdev(filled_downsized_data)

        # Hacky adjustment of tolerance for coarse rasterization
        std_tol = 0.2 if (filled_downsized_data.size > 100 and ratio_diff > 0.1) else 0.6
        stnaratio_eval = True if abs(nstdev_raw_data - nstdev_downsized_data) <= std_tol else False

    eval_summary = True if (ratio_eval & nq_evals & stnaratio_eval) else False
    return eval_summary
