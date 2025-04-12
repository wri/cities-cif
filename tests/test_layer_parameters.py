from _ast import FunctionDef
from ast import parse, walk

import pytest
import xarray as xr
import numpy as np
from skimage.metrics import structural_similarity as ssim
from pyproj import CRS
from city_metrix.layers import *
from city_metrix.layers.layer_geometry import GeoExtent
from tests.resources.bbox_constants import BBOX_BRA_LAURO_DE_FREITAS_1
from tests.tools.general_tools import get_class_from_instance, get_class_default_spatial_resolution

COUNTRY_CODE_FOR_BBOX = 'BRA'
BBOX = BBOX_BRA_LAURO_DE_FREITAS_1
RESOLUTION_TOLERANCE = 1
DOWNSIZE_FACTOR = 2

class TestSpatialResolution:
    """
    Evaluation of spatial_resolution property
    To add a test for a scalable layer that has the spatial_resolution property:
    1. Add the class name to the city_metrix.layers import statement above
    2. Copy an existing test_*_spatial_resolution() test
       a. rename for the new layer
       b. specify a minimal class instance for the layer, not specifying the spatial_resolution attribute.
    """

    def test_albedo_downsampled_spatial_resolution(self):
        class_instance = Albedo()
        default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = (
            _get_sample_data(class_instance, BBOX, DOWNSIZE_FACTOR))
        downsizing_is_within_tolerances = _evaluate_raster_value(default_res_data, downsized_res_data)

        assert pytest.approx(target_downsized_res, rel=RESOLUTION_TOLERANCE) == estimated_actual_res
        assert downsizing_is_within_tolerances

    def test_alos_dsm_downsampled_spatial_resolution(self):
        class_instance = AlosDSM()
        default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = (
            _get_sample_data(class_instance, BBOX, DOWNSIZE_FACTOR))
        downsizing_is_within_tolerances = _evaluate_raster_value(default_res_data, downsized_res_data)

        assert pytest.approx(target_downsized_res, rel=RESOLUTION_TOLERANCE) == estimated_actual_res
        assert downsizing_is_within_tolerances

    def test_average_net_building_height_downsampled_spatial_resolution(self):
        class_instance = AverageNetBuildingHeight()
        default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = (
            _get_sample_data(class_instance, BBOX, DOWNSIZE_FACTOR))
        downsizing_is_within_tolerances = _evaluate_raster_value(default_res_data, downsized_res_data)

        assert pytest.approx(target_downsized_res, rel=RESOLUTION_TOLERANCE) == estimated_actual_res
        assert downsizing_is_within_tolerances

    def test_built_up_height_downsampled_spatial_resolution(self):
        class_instance = BuiltUpHeight()
        default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = (
            _get_sample_data(class_instance, BBOX, DOWNSIZE_FACTOR))
        downsizing_is_within_tolerances = _evaluate_raster_value(default_res_data, downsized_res_data)

        assert pytest.approx(target_downsized_res, rel=RESOLUTION_TOLERANCE) == estimated_actual_res
        assert downsizing_is_within_tolerances

    def test_esa_world_cover_downsampled_spatial_resolution(self):
        class_instance = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
        default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = (
            _get_sample_data(class_instance, BBOX, DOWNSIZE_FACTOR))
        downsizing_is_within_tolerances = _evaluate_raster_value(default_res_data, downsized_res_data)

        assert pytest.approx(target_downsized_res, rel=RESOLUTION_TOLERANCE) == estimated_actual_res
        assert downsizing_is_within_tolerances

    def test_high_land_surface_temperature_downsampled_spatial_resolution(self):
        class_instance = HighLandSurfaceTemperature()
        default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = (
            _get_sample_data(class_instance, BBOX, DOWNSIZE_FACTOR))
        downsizing_is_within_tolerances = _evaluate_raster_value(default_res_data, downsized_res_data)

        assert pytest.approx(target_downsized_res, rel=RESOLUTION_TOLERANCE) == estimated_actual_res
        assert downsizing_is_within_tolerances

    def test_impervious_surface_downsampled_spatial_resolution(self):
        class_instance = ImperviousSurface()
        default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = (
            _get_sample_data(class_instance, BBOX, DOWNSIZE_FACTOR))
        downsizing_is_within_tolerances = _evaluate_raster_value(default_res_data, downsized_res_data)

        assert pytest.approx(target_downsized_res, rel=RESOLUTION_TOLERANCE) == estimated_actual_res
        assert downsizing_is_within_tolerances

    def test_land_surface_temperature_downsampled_spatial_resolution(self):
        class_instance = LandSurfaceTemperature()
        default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = (
            _get_sample_data(class_instance, BBOX, DOWNSIZE_FACTOR))
        downsizing_is_within_tolerances = _evaluate_raster_value(default_res_data, downsized_res_data)

        assert pytest.approx(target_downsized_res, rel=RESOLUTION_TOLERANCE) == estimated_actual_res
        assert downsizing_is_within_tolerances

    def test_nasa_dem_downsampled_spatial_resolution(self):
        class_instance = NasaDEM()
        default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = (
            _get_sample_data(class_instance, BBOX, DOWNSIZE_FACTOR))
        downsizing_is_within_tolerances = _evaluate_raster_value(default_res_data, downsized_res_data)

        assert pytest.approx(target_downsized_res, rel=RESOLUTION_TOLERANCE) == estimated_actual_res
        assert downsizing_is_within_tolerances

    def test_natural_areas_downsampled_spatial_resolution(self):
        class_instance = NaturalAreas()
        default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = (
            _get_sample_data(class_instance, BBOX, DOWNSIZE_FACTOR))
        downsizing_is_within_tolerances = _evaluate_raster_value(default_res_data, downsized_res_data)

        assert pytest.approx(target_downsized_res, rel=RESOLUTION_TOLERANCE) == estimated_actual_res
        assert downsizing_is_within_tolerances

    def test_ndvi_sentinel2_downsampled_spatial_resolution(self):
        class_instance = NdviSentinel2(year=2023)
        default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = (
            _get_sample_data(class_instance, BBOX, DOWNSIZE_FACTOR))
        downsizing_is_within_tolerances = _evaluate_raster_value(default_res_data, downsized_res_data)

        assert pytest.approx(target_downsized_res, rel=RESOLUTION_TOLERANCE) == estimated_actual_res
        assert downsizing_is_within_tolerances

    def test_tree_canopy_height_downsampled_spatial_resolution(self):
        class_instance = TreeCanopyHeight()
        default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = (
            _get_sample_data(class_instance, BBOX, DOWNSIZE_FACTOR))
        downsizing_is_within_tolerances = _evaluate_raster_value(default_res_data, downsized_res_data)

        assert pytest.approx(target_downsized_res, rel=RESOLUTION_TOLERANCE) == estimated_actual_res
        assert downsizing_is_within_tolerances

    def test_tree_cover_downsampled_spatial_resolution(self):
        class_instance = TreeCover()
        default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = (
            _get_sample_data(class_instance, BBOX, DOWNSIZE_FACTOR))
        downsizing_is_within_tolerances = _evaluate_raster_value(default_res_data, downsized_res_data)

        assert pytest.approx(target_downsized_res, rel=RESOLUTION_TOLERANCE) == estimated_actual_res
        assert downsizing_is_within_tolerances

    def test_urban_land_use_downsampled_spatial_resolution(self):
        class_instance = UrbanLandUse()
        default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = (
            _get_sample_data(class_instance, BBOX, DOWNSIZE_FACTOR))
        downsizing_is_within_tolerances = _evaluate_raster_value(default_res_data, downsized_res_data)

        assert pytest.approx(target_downsized_res, rel=RESOLUTION_TOLERANCE) == estimated_actual_res
        assert downsizing_is_within_tolerances

    def test_world_pop_downsampled_spatial_resolution(self):
        class_instance = WorldPop()
        default_res_data, downsized_res_data, target_downsized_res, estimated_actual_res = (
            _get_sample_data(class_instance, BBOX, DOWNSIZE_FACTOR))
        downsizing_is_within_tolerances = _evaluate_raster_value(default_res_data, downsized_res_data)

        assert pytest.approx(target_downsized_res, rel=RESOLUTION_TOLERANCE) == estimated_actual_res
        assert downsizing_is_within_tolerances

    def test_halved_up_sampled_spatial_resolution(self):
        class_instance = Albedo()
        halved_default_resolution = get_class_default_spatial_resolution(class_instance) / 2

        expected_resolution = halved_default_resolution
        modified_data = _get_modified_resolution_data(class_instance, halved_default_resolution, BBOX)
        estimated_actual_resolution = _estimate_spatial_resolution(modified_data)

        assert expected_resolution == estimated_actual_resolution

    def test_null_spatial_resolution(self):
        class_instance = Albedo()
        spatial_resolution=None

        try:
            _get_modified_resolution_data(class_instance, spatial_resolution, BBOX)
        except Exception as e:
            pytest.fail(f"get_data() raised {type(e).__name__} unexpectedly!")


class TestOtherParameters:
    def test_albedo_threshold(self):
        threshold=0.1
        data = Albedo(threshold=threshold).get_data(BBOX)
        max_albedo = data.values[~np.isnan(data.values)].max()

        assert threshold > max_albedo,\
            f"Maximum value ({max_albedo}) in Albedo dataset is not < threshold of {threshold}."

    def test_albedo_dates(self):
        with pytest.raises(Exception) as e_info:
            Albedo(start_date="2021-01-01", end_date="2021-01-02").get_data(BBOX)
        msg_correct = False if str(e_info.value).find("max() arg is an empty sequence") == -1 else True
        assert msg_correct

        with pytest.raises(Exception) as e_info:
            Albedo(start_date="2021-01-01", end_date=None).get_data(BBOX)
        msg_correct = False if str(e_info.value).find("max() arg is an empty sequence") == -1 else True
        assert msg_correct

    def test_high_land_surface_temperature_dates(self):
        with pytest.raises(Exception) as e_info:
            HighLandSurfaceTemperature(start_date="2021-01-01", end_date="2021-01-02").get_data(BBOX)
        msg_correct = False if str(e_info.value).find("Dictionary does not contain key: 'date'") == -1 else True
        assert msg_correct

    def test_land_surface_temperature_dates(self):
        with pytest.raises(Exception) as e_info:
            LandSurfaceTemperature(start_date="2021-01-01", end_date="2021-01-02").get_data(BBOX)
        msg_correct = False if str(e_info.value).find("max() arg is an empty sequence") == -1 else True
        assert msg_correct

        with pytest.raises(Exception) as e_info:
            LandSurfaceTemperature(start_date="2021-01-01", end_date=None).get_data(BBOX)
        msg_correct = False if str(e_info.value).find("max() arg is an empty sequence") == -1 else True
        assert msg_correct

    def test_ndvi_sentinel2_dates(self):
        with pytest.raises(Exception) as e_info:
            data = NdviSentinel2(year=None).get_data(BBOX)
        msg_correct = False if str(e_info.value).find("get_data() requires a year value") == -1 else True
        assert msg_correct

        with pytest.raises(Exception) as e_info:
            NdviSentinel2(year="1970").get_data(BBOX)
        msg_correct = False if str(e_info.value).find("max() arg is an empty sequence") == -1 else True
        assert msg_correct

    def test_open_buildings_country(self):
        with pytest.raises(Exception) as e_info:
            OpenBuildings(country="ZZZ").get_data(BBOX)

        msg_correct = False if str(e_info.value).find("projects/sat-io/open-datasets/VIDA_COMBINED/ZZZ' not found.") == -1 else True
        assert msg_correct

    def test_tree_cover_min_max_cover(self):
        data = TreeCover(min_tree_cover = 150).get_data(BBOX)
        non_null_cells = len(data.values[~np.isnan(data)])
        assert non_null_cells == 0

        data = TreeCover(max_tree_cover = -1).get_data(BBOX)
        non_null_cells = len(data.values[~np.isnan(data)])
        assert non_null_cells == 0


def test_function_validate_layer_instance():
    is_valid, except_str = _validate_layer_instance('t')
    assert is_valid is False
    is_valid, except_str = _validate_layer_instance(EsaWorldCoverClass.BUILT_UP)
    assert is_valid is False
    is_valid, except_str = _validate_layer_instance(OpenStreetMap())
    assert is_valid is False
    is_valid, except_str = _validate_layer_instance(Albedo())
    assert is_valid is True

def _get_sample_data(class_instance, bbox: GeoExtent, downsize_factor):
    is_valid, except_str = _validate_layer_instance(class_instance)
    if is_valid is False:
        raise Exception(except_str)

    default_res = get_class_default_spatial_resolution(class_instance)
    downsized_resolution = downsize_factor * default_res

    downsized_res_data = _get_modified_resolution_data(class_instance, downsized_resolution, bbox)
    default_res_data = _get_modified_resolution_data(class_instance, default_res, bbox)

    estimated_actual_resolution = _estimate_spatial_resolution(downsized_res_data)

    return default_res_data, downsized_res_data, downsized_resolution, estimated_actual_resolution

def _get_crs_from_image_data(image_data):
    if isinstance(image_data, xr.DataArray):
        crs_string = image_data.rio.crs.wkt
    else:
        crs_string = image_data.crs
    crs = CRS.from_string(crs_string)
    return crs


def _get_modified_resolution_data(class_instance, spatial_resolution, bbox):
    data = class_instance.get_data(bbox, spatial_resolution=spatial_resolution)
    return data

def _validate_layer_instance(obj):
    is_valid = True
    except_str = None

    if not obj.__class__.__bases__[0] == Layer:
        is_valid = False
        except_str = "Specified object '%s' is not a valid Layer class instance." % obj
    else:
        cls = get_class_from_instance(obj)
        cls_name = type(cls).__name__

        obj_spatial_resolution = get_class_default_spatial_resolution(obj)
        cls_default_spatial_resolution = get_class_default_spatial_resolution(cls)

        if not cls_default_spatial_resolution:
            is_valid = False
            except_str = f"Class '{cls_name}' does not have spatial_resolution property."
        elif not obj_spatial_resolution == cls_default_spatial_resolution:
            is_valid = False
            except_str = f"Do not specify spatial_resolution property value for class '{cls_name}'."
        elif not obj_spatial_resolution:
            is_valid = False
            except_str = f"Signature of object {cls_name} must specify a non-null default value for spatial_resolution. Please correct."

    return is_valid, except_str

def _estimate_spatial_resolution(data):
    y_cells = float(data['y'].size - 1)
    y_min = data.coords['y'].values.min()
    y_max = data.coords['y'].values.max()

    crs = _get_crs_from_image_data(data)
    crs_unit = crs.axis_info[0].unit_name

    if crs_unit == 'metre':
        diff_distance = y_max - y_min
    else:
        raise Exception('Unhandled projection units: %s for projection: %s' % (crs_unit, crs.srs))

    estimated_actual_resolution = round(diff_distance / y_cells)

    return estimated_actual_resolution

def _get_populated_fraction(dataset):
    raw_data_size = dataset.values.size
    populated_raw_data = dataset.values[(~np.isnan(dataset.values)) & (dataset.values > 0)]
    populated_data_raw_size = populated_raw_data.size
    populated_raw_data_fraction = populated_data_raw_size/raw_data_size
    return populated_raw_data_fraction

def _evaluate_raster_value(raw_data, downsized_data):
    # Below values where determined through trial and error evaluation of results in QGIS
    populated_fraction_tolerance = 0.2
    normalized_rmse_tolerance = 0.3

    populated_raw_data_ratio = _get_populated_fraction(raw_data)
    populated_downsized_data_ratio = _get_populated_fraction(raw_data)
    populated_fraction_diff = abs(populated_raw_data_ratio - populated_downsized_data_ratio)
    populated_fraction_eval = True if populated_fraction_diff <= populated_fraction_tolerance else False

    filled_raw_data = raw_data.fillna(0)
    filled_downsized_data = downsized_data.fillna(0)

    # Resample raw_data to match the resolution of the downsized_data.
    # This operation is necessary in order to use RMSE and SSIM since they require matching array dimensions.
    # Interpolation is set to quadratic method to intentionally not match method used by xee. (TODO Find documentation)
    # For future releases of this method, we may need to control the interpolation to match what was used
    # for a specific layer.
    # Note: Initial investigations using the unresampled-raw and downsized data with evaluation by
    # mean value, quantiles,and standard deviation were unsuccessful due to false failures on valid downsized images.
    resampled_filled_raw_data = (filled_raw_data
                                 .interp_like(filled_downsized_data, method='linear')
                                 .fillna(0))

    # Convert xarray DataArrays to numpy arrays
    processed_raw_data_np = resampled_filled_raw_data.values
    processed_downsized_data_np = filled_downsized_data.values

    # Calculate and evaluate normalized Root Mean Squared Error (RMSE)
    max_val = processed_downsized_data_np.max() \
        if processed_downsized_data_np.max() > processed_raw_data_np.max() else processed_raw_data_np.max()
    normalized_rmse = np.sqrt(np.mean(np.square(processed_downsized_data_np - processed_raw_data_np))) / max_val
    matching_rmse = True if normalized_rmse < normalized_rmse_tolerance else False

    # Calculate and evaluate Structural Similarity Index (SSIM)
    # Progressively decrease criteria for asserting a match as raster count decreases and null values increase
    if processed_downsized_data_np.size > 100:
        if populated_fraction_diff <= 0.1:
            ssim_index_tolerance = 0.6
        else:
            ssim_index_tolerance = 0.4
    else:
        ssim_index_tolerance = 0.3
    ssim_index, _ = ssim(processed_downsized_data_np, processed_raw_data_np, full=True, data_range=max_val)
    matching_ssim = True if round(ssim_index,1) >= ssim_index_tolerance else False

    results_match = True if (populated_fraction_eval & matching_rmse & matching_ssim) else False

    return results_match
