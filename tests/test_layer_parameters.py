from city_metrix.layers import (
    Layer,
    Albedo,
    AlosDSM,
    AverageNetBuildingHeight,
    BuiltUpHeight,
    EsaWorldCover,
    EsaWorldCoverClass,
    LandSurfaceTemperature,
    NasaDEM,
    NaturalAreas,
    NdviSentinel2,
    TreeCanopyHeight,
    TreeCover,
    UrbanLandUse,
    WorldPop
)
from tests.resources.bbox_constants import BBOX_BRA_LAURO_DE_FREITAS_1

"""
Note: To add a test for another scalable layer that has the spatial_resolution property:
1. Add the class name to the city_metrix.layers import statement above
2. Specify a minimal class instance in the set below. Do no specify the spatial_resolution
   property in the instance definition.
"""
CLASSES_WITH_spatial_resolution_PROPERTY = \
    {
        # 'Albedo()',
        # 'AlosDSM()',
        # 'AverageNetBuildingHeight()',
        # 'BuiltUpHeight()',
        'EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)',
        # 'LandSurfaceTemperature()',
        # 'NasaDEM()',
        # 'NaturalAreas()',
        # 'NdviSentinel2(year=2023)',
        # 'TreeCanopyHeight()',
        # 'TreeCover()',
        # 'UrbanLandUse()',
        # 'WorldPop()'
    }

COUNTRY_CODE_FOR_BBOX = 'BRA'
BBOX = BBOX_BRA_LAURO_DE_FREITAS_1

def test_spatial_resolution_for_all_scalable_layers():
    for class_instance_str in CLASSES_WITH_spatial_resolution_PROPERTY:
        is_valid, except_str = validate_layer_instance(class_instance_str)
        if is_valid is False:
            raise Exception(except_str)

        class_instance = eval(class_instance_str)

        # Double the spatial_resolution for the specified Class
        doubled_default_resolution = 2 * class_instance.spatial_resolution
        class_instance.spatial_resolution=doubled_default_resolution

        evaluate_layer(class_instance, doubled_default_resolution)


def test_function_validate_layer_instance():
    is_valid, except_str = validate_layer_instance(Albedo())
    assert is_valid is False
    is_valid, except_str = validate_layer_instance('t')
    assert is_valid is False
    is_valid, except_str = validate_layer_instance('Layer()')
    assert is_valid is False
    is_valid, except_str = validate_layer_instance('OpenStreetMap()')
    assert is_valid is False
    is_valid, except_str = validate_layer_instance('Albedo(spatial_resolution = 2)')
    assert is_valid is False

def validate_layer_instance(obj_string):
    is_valid = True
    except_str = None
    obj_eval = None

    if not type(obj_string) == str:
        is_valid = False
        except_str = "Specified object '%s' must be specified as a string." % obj_string
        return is_valid, except_str

    try:
        obj_eval = eval(obj_string)
    except:
        is_valid = False
        except_str = "Specified object '%s' is not a class instance." % obj_string
        return is_valid, except_str

    if not type(obj_eval).__bases__[0] == Layer:
        is_valid = False
        except_str = "Specified object '%s' is not a valid Layer class instance." % obj_string
    elif not hasattr(obj_eval, 'spatial_resolution'):
        is_valid = False
        except_str = "Specified class '%s' does not have the spatial_resolution property." % obj_string
    elif not obj_string.find('spatial_resolution') == -1:
        is_valid = False
        except_str = "Do not specify spatial_resolution property value in object '%s'." % obj_string
    elif obj_eval.spatial_resolution is None:
        is_valid = False
        except_str = "Class signature cannot specify None for default value for class."

    return is_valid, except_str

def evaluate_layer(layer, expected_resolution):
    data = layer.get_data(BBOX)
    actual_estimated_resolution, y_cells, y_min, y_max = get_resolution_estimate(data)
    print ('y_cells %s, y_min %s, y_max %s' % (y_cells, y_min, y_max))
    assert expected_resolution == actual_estimated_resolution

def get_resolution_estimate(data):
    y_cells = float(data['y'].size - 1)
    y_min = data['y'].values.min()
    y_max = data['y'].values.max()
    y_diff = y_max - y_min
    ry = round(y_diff/y_cells)
    return ry, y_cells, y_min, y_max
