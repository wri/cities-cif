import math
import utm
from typing import Union
from enum import Enum

from dask.diagnostics import ProgressBar
from ee import ImageCollection
from pyproj import CRS
from shapely.geometry import point

from city_metrix.constants import WGS_EPSG_CODE, ProjectionType, WGS_CRS


def parse_city_aoi_json(json_str):
    import json
    data = json.loads(json_str)
    city_id = data['city_id']
    aoi_id = data['aoi_id']
    return city_id, aoi_id

def construct_city_aoi_json(city_id, aoi_id):
    json_str = f'{{"city_id": "{city_id}", "aoi_id": "{aoi_id}"}}'
    return json_str

# ================= Projection related =====================
def get_crs_from_data(data):
    crs_wkt = data.spatial_ref.crs_wkt
    epsg_code = CRS.from_wkt(crs_wkt).to_epsg()
    crs = f'EPSG:{epsg_code}'
    return crs

def reproject_units(min_x, min_y, max_x, max_y, from_crs, to_crs):
    """
    Project coordinates from one map EPSG projection to another
    """
    from pyproj import Transformer
    transformer = Transformer.from_crs(from_crs, to_crs)

    # Note: order of coordinates must be lat/lon
    sw_coord = transformer.transform(min_x, min_y)
    ne_coord = transformer.transform(max_x, max_y)

    reproj_min_x = float(sw_coord[0])
    reproj_min_y = float(sw_coord[1])
    reproj_max_x = float(ne_coord[0])
    reproj_max_y = float(ne_coord[1])

    reproj_bbox = (reproj_min_y, reproj_min_x, reproj_max_y, reproj_max_x)
    return reproj_bbox

def get_utm_zone_from_latlon_point(sample_point: point) -> str:
    """
    Get the UTM zone projection for given geographic point.
    :param sample_point: a shapely point specified in geographic coordinates
    :return: the crs (EPSG code) for the UTM zone of the point
    """

    utm_x, utm_y, band, zone = utm.from_latlon(sample_point.y, sample_point.x)

    if sample_point.y > 0:  # Northern zone
        epsg = 32600 + band
    else:
        epsg = 32700 + band

    return f"EPSG:{epsg}"

def get_projection_type(crs: Union[str | int]):
    if isinstance(crs, str):
        if crs.lower().startswith('epsg:'):
            epsg_code = int(crs.split(':')[1])
        else:
            try:
                epsg_code = CRS.from_wkt(crs).to_epsg()
            except:
                raise Exception("Valid crs string must be specified in form of ('EPSG:n') or a crs-wkt.")

    elif isinstance(crs, int):
        epsg_code = crs
    else:
        raise ValueError(f"Value of ({crs}) is an invalid crs string or epsg code. ")

    if epsg_code == WGS_EPSG_CODE:
        projection_type = ProjectionType.GEOGRAPHIC
    elif 32601 <= epsg_code <= 32660 or 32701 <= epsg_code <= 32760:
        projection_type = ProjectionType.UTM
    else:
        raise ValueError(f"CRS ({crs}) not supported.")

    return projection_type

# ============ Object naming ================================
DATE_ATTRIBUTES = ['year', 'start_year', 'start_date', 'end_year', 'end_date']

def build_cache_layer_names(layer_obj):
    """
    Function uses the sequence of layer-class parameters specified in two class constants, plus standard date
    parameters in many of the layer classes to construct names for cache folders and cached layer files.
    """
    primary_qualifiers = _build_naming_string_from_attribute_list(layer_obj, layer_obj.MAJOR_NAMING_ATTS)
    secondary_qualifiers = _build_naming_string_from_attribute_list(layer_obj, layer_obj.MINOR_NAMING_ATTS)

    class_name = layer_obj.__class__.__name__
    date_kv_string = _build_naming_string_from_standard_parameters(layer_obj)
    file_format = layer_obj.GEOSPATIAL_FILE_FORMAT

    layer_folder_name = f"{class_name}{primary_qualifiers}"
    layer_id = f"{layer_folder_name}{secondary_qualifiers}{date_kv_string}.{file_format}"

    return layer_folder_name, layer_id


def _build_naming_string_from_attribute_list(layer_obj, naming_atts):
    """
    Function takes the list of layer-class attributes, converts the attribute name to Pascal-case,
    appends the object parameter value, and constructs a name-value string to be used as part of the
    cif-cache storage folder name and layer file name.
    """
    qualifier_name = ""
    if not (naming_atts is None or naming_atts == ""):
        for attribute in naming_atts:
            if attribute.lower() not in DATE_ATTRIBUTES:
                value = eval(f"layer_obj.{attribute}")
                flat_value = _flatten_attribute_value(value)
                if flat_value is not None:
                    pascal_key = _convert_snake_case_to_pascal_case(attribute)
                    param_name = _construct_kv_string(pascal_key, flat_value)
                    qualifier_name += param_name
    return qualifier_name


def _build_naming_string_from_standard_parameters(layer_obj):
    """
    Function takes the values from standard date attributes in a layer-class and constructs a name-value string
    to be used as part of the cif-cache layer file name.
    """
    date_kv_string = ""
    for key, value in layer_obj.__dict__.items():
        for att in DATE_ATTRIBUTES:
            string_val = _construct_naming_string_from_date_attribute(key, value, att)
            date_kv_string += string_val if string_val is not None else ""

    return date_kv_string


def _construct_naming_string_from_date_attribute(key, value, search_key_name):
    date_kv_name = None
    if key == search_key_name:
        pascal_key_name = _convert_snake_case_to_pascal_case(key)
        date_kv_name = _construct_kv_string(pascal_key_name, value)

    return date_kv_name


def _flatten_attribute_value(value):
    """
    Function reformats attribute values into a string that can be used for naming a layer folder or file.
    For example, the function takes a list of attribute values and concatenates them into a dash-delimited string.
    """
    import numbers
    if value is None or value == "" or value == []:
        flattened_value = None
    elif isinstance(value, Enum):
        flattened_value = value.name
    elif isinstance(value, str) or isinstance(value, numbers.Number):
        if isinstance(value, float):
            flattened_value = str(value).replace('.','')
        else:
            flattened_value = value
    elif isinstance(value, list):
        flattened_value = '-'.join(value)
    else:
        raise Exception("Qualifier name could not be determined.")

    return flattened_value


def _convert_snake_case_to_pascal_case(attribute_name):
    pascal_name = attribute_name.replace("_", " ").title().replace(" ", "")
    return pascal_name

def _construct_kv_string(key, value):
    return f"__{key}_{value}"


#  ================ Misc ======================
def standardize_y_dimension_direction(data_array):
    """
    Function resets y-values so they comply with the standard GDAL top-down increasing order, as needed.
    """
    was_reversed= False
    y_dimensions = data_array.shape[0]
    if data_array.y.data[0] < data_array.y.data[y_dimensions - 1]:
        data_array = data_array.isel({data_array.rio.y_dim: slice(None, None, -1)})
        was_reversed = True
    return was_reversed, data_array

def get_haversine_distance(lon1, lat1, lon2, lat2):
    # Global-average radius of the Earth in meters
    R = 6371000

    # Convert degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in meters
    distance = R * c

    return distance

