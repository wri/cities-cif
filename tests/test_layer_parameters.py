import pytest
from pyproj import CRS
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
RESOLUTION_TOLERANCE = 1

def test_albedo_spatial_resolution():
    class_instance = Albedo()
    doubled_default_resolution, actual_estimated_resolution =  evaluate_doubled_resolution_property(class_instance)
    assert pytest.approx(doubled_default_resolution, rel=RESOLUTION_TOLERANCE) == actual_estimated_resolution

def test_alos_dsm_spatial_resolution():
    class_instance = AlosDSM()
    doubled_default_resolution, actual_estimated_resolution =  evaluate_doubled_resolution_property(class_instance)
    assert pytest.approx(doubled_default_resolution, rel=RESOLUTION_TOLERANCE) == actual_estimated_resolution

def test_average_net_building_height_spatial_resolution():
    class_instance = AverageNetBuildingHeight()
    doubled_default_resolution, actual_estimated_resolution =  evaluate_doubled_resolution_property(class_instance)
    assert pytest.approx(doubled_default_resolution, rel=RESOLUTION_TOLERANCE) == actual_estimated_resolution

def test_built_up_height_spatial_resolution():
    class_instance = BuiltUpHeight()
    doubled_default_resolution, actual_estimated_resolution =  evaluate_doubled_resolution_property(class_instance)
    assert pytest.approx(doubled_default_resolution, rel=RESOLUTION_TOLERANCE) == actual_estimated_resolution

def test_esa_world_cover_spatial_resolution():
    class_instance = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
    doubled_default_resolution, actual_estimated_resolution =  evaluate_doubled_resolution_property(class_instance)
    assert pytest.approx(doubled_default_resolution, rel=RESOLUTION_TOLERANCE) == actual_estimated_resolution

def test_high_land_surface_temperature_spatial_resolution():
    class_instance = HighLandSurfaceTemperature()
    doubled_default_resolution, actual_estimated_resolution =  evaluate_doubled_resolution_property(class_instance)
    assert pytest.approx(doubled_default_resolution, rel=RESOLUTION_TOLERANCE) == actual_estimated_resolution

def test_land_surface_temperature_spatial_resolution():
    class_instance = LandSurfaceTemperature()
    doubled_default_resolution, actual_estimated_resolution =  evaluate_doubled_resolution_property(class_instance)
    assert pytest.approx(doubled_default_resolution, rel=RESOLUTION_TOLERANCE) == actual_estimated_resolution

def test_nasa_dem_spatial_resolution():
    class_instance = NasaDEM()
    doubled_default_resolution, actual_estimated_resolution =  evaluate_doubled_resolution_property(class_instance)
    assert pytest.approx(doubled_default_resolution, rel=RESOLUTION_TOLERANCE) == actual_estimated_resolution

def test_natural_areas_spatial_resolution():
    class_instance = NaturalAreas()
    doubled_default_resolution, actual_estimated_resolution =  evaluate_doubled_resolution_property(class_instance)
    assert pytest.approx(doubled_default_resolution, rel=RESOLUTION_TOLERANCE) == actual_estimated_resolution

def test_ndvi_sentinel2_spatial_resolution():
    class_instance = NdviSentinel2(year=2023)
    doubled_default_resolution, actual_estimated_resolution =  evaluate_doubled_resolution_property(class_instance)
    assert pytest.approx(doubled_default_resolution, rel=RESOLUTION_TOLERANCE) == actual_estimated_resolution

def test_tree_canopy_height_spatial_resolution():
    class_instance = TreeCanopyHeight()
    doubled_default_resolution, actual_estimated_resolution =  evaluate_doubled_resolution_property(class_instance)
    assert pytest.approx(doubled_default_resolution, rel=RESOLUTION_TOLERANCE) == actual_estimated_resolution

def test_tree_cover_spatial_resolution():
    class_instance = TreeCover()
    doubled_default_resolution, actual_estimated_resolution =  evaluate_doubled_resolution_property(class_instance)
    assert pytest.approx(doubled_default_resolution, rel=RESOLUTION_TOLERANCE) == actual_estimated_resolution

def test_urban_land_use_spatial_resolution():
    class_instance = UrbanLandUse()
    doubled_default_resolution, actual_estimated_resolution =  evaluate_doubled_resolution_property(class_instance)
    assert pytest.approx(doubled_default_resolution, rel=RESOLUTION_TOLERANCE) == actual_estimated_resolution

def test_world_pop_spatial_resolution():
    class_instance = WorldPop()
    doubled_default_resolution, actual_estimated_resolution =  evaluate_doubled_resolution_property(class_instance)
    assert pytest.approx(doubled_default_resolution, rel=RESOLUTION_TOLERANCE) == actual_estimated_resolution

def test_halved_spatial_resolution():
    class_instance = Albedo()
    halved_default_resolution = get_class_default_spatial_resolution(class_instance) / 2
    class_instance.spatial_resolution=halved_default_resolution

    expected_resolution = halved_default_resolution
    estimated_actual_resolution = get_modified_resolution_data(class_instance)

    assert expected_resolution == estimated_actual_resolution

def test_null_spatial_resolution():
    class_instance = Albedo()
    class_instance.spatial_resolution=None

    with pytest.raises(Exception) as e_info:
        get_modified_resolution_data(class_instance)

def test_function_validate_layer_instance():
    is_valid, except_str = validate_layer_instance('t')
    assert is_valid is False
    is_valid, except_str = validate_layer_instance(EsaWorldCoverClass.BUILT_UP)
    assert is_valid is False
    is_valid, except_str = validate_layer_instance(OpenStreetMap())
    assert is_valid is False
    is_valid, except_str = validate_layer_instance(Albedo(spatial_resolution = 2))
    assert is_valid is False

def evaluate_doubled_resolution_property(obj):
    is_valid, except_str = validate_layer_instance(obj)
    if is_valid is False:
        raise Exception(except_str)

    # Double the default scale for testing
    doubled_default_resolution = 2 * get_class_default_spatial_resolution(obj)
    obj.spatial_resolution=doubled_default_resolution

    expected_resolution = doubled_default_resolution
    estimated_actual_resolution = get_modified_resolution_data(obj)

    return expected_resolution, estimated_actual_resolution

def get_modified_resolution_data(obj):
    data = obj.get_data(BBOX)
    estimated_actual_resolution = estimate_spatial_resolution(data)

    return estimated_actual_resolution


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

    crs_string = data.rio.crs.data['init']
    crs = CRS.from_string(crs_string)
    crs_unit = crs.axis_info[0].unit_name

    if crs_unit == 'metre':
        diff_distance = y_max - y_min
    else:
        raise Exception('Unhandled projection units: %s for projection: %s' % (crs_unit, crs_string))

    estimated_actual_resolution = round(diff_distance / y_cells)

    return estimated_actual_resolution
