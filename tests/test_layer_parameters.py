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
    WorldPop, OpenStreetMap
)
from tests.resources.bbox_constants import BBOX_BRA_LAURO_DE_FREITAS_1
from tests.tools.spatial_tools import get_distance_between_geocoordinates

"""
Note: To add a test for another scalable layer that has the spatial_resolution property:
1. Add the class name to the city_metrix.layers import statement above
2. Specify a minimal class instance in the set below. Do no specify the spatial_resolution
   property in the instance definition.
"""
CLASSES_WITH_SPATIAL_RESOLUTION_PROPERTY = \
    {
        Albedo(),
        AlosDSM(),
        AverageNetBuildingHeight(),
        BuiltUpHeight(),
        EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP),
        LandSurfaceTemperature(),
        NasaDEM(),
        NaturalAreas(),
        NdviSentinel2(year=2023),
        TreeCanopyHeight(),
        TreeCover(),
        UrbanLandUse(),
        WorldPop()
    }

COUNTRY_CODE_FOR_BBOX = 'BRA'
BBOX = BBOX_BRA_LAURO_DE_FREITAS_1

def test_spatial_resolution_for_all_scalable_layers():
    for obj in CLASSES_WITH_SPATIAL_RESOLUTION_PROPERTY:
        is_valid, except_str = validate_layer_instance(obj)
        if is_valid is False:
            raise Exception(except_str)

        cls = get_class_from_instance(obj)

        # Double the spatial_resolution for the specified Class
        doubled_default_resolution = 2 * cls.spatial_resolution
        obj.spatial_resolution=doubled_default_resolution

        evaluate_layer(obj, doubled_default_resolution)


def test_function_validate_layer_instance():
    is_valid, except_str = validate_layer_instance('t')
    assert is_valid is False
    is_valid, except_str = validate_layer_instance(EsaWorldCoverClass.BUILT_UP)
    assert is_valid is False
    is_valid, except_str = validate_layer_instance(OpenStreetMap())
    assert is_valid is False
    is_valid, except_str = validate_layer_instance(Albedo(spatial_resolution = 2))
    assert is_valid is False

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

def get_class_from_instance(obj):
    cls = obj.__class__()
    return cls

def evaluate_layer(layer, expected_resolution):
    data = layer.get_data(BBOX)
    actual_estimated_resolution = estimate_spatial_resolution(data)
    assert expected_resolution == actual_estimated_resolution

def estimate_spatial_resolution(data):
    y_cells = float(data['y'].size - 1)

    y_min = data['y'].values.min()
    y_max = data['y'].values.max()

    try:
        crs = CRS.from_string(data.crs)
        crs_units = crs.axis_info[0].unit_name
    except:
        # if xarray doesn't have crs property, assume meters
        crs_units = 'metre'

    if crs_units == 'metre':
        y_diff = y_max - y_min
    elif crs_units == 'foot':
        feet_to_meter = 0.3048
        y_diff = (y_max - y_min) * feet_to_meter
    elif crs_units == 'degree':
        lat1 = y_min
        lat2 = y_max
        lon1 = data['x'].values.min()
        lon2 = lon1
        y_diff = get_distance_between_geocoordinates(lat1, lon1, lat2, lon2)
    else:
        raise Exception('Unhandled projection units: %s' % crs_units)

    ry = round(y_diff / y_cells)

    return ry
