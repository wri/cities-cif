import math
import os
from datetime import datetime
from enum import Enum

import geopandas as gpd
from typing import Union
from pyproj import CRS

from city_metrix.constants import WGS_EPSG_CODE, production_aws_bucket, production_s3_aws_profile


def set_production_environment_variables():
    set_environment_variable('AWS_BUCKET', production_aws_bucket)
    set_environment_variable('S3_AWS_PROFILE', production_s3_aws_profile)

def set_environment_variable(variable_name, variable_value):
    os.environ[variable_name] = variable_value

def get_geojson_geometry_bounds(geojson: str):
    gdf = gpd.GeoDataFrame.from_features(geojson)
    return gdf.total_bounds

def get_projection_name(crs: Union[str|int]):
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
        projection_name = 'geographic'
    elif 32601 <= epsg_code <= 32660 or 32701 <= epsg_code <= 32760:
        projection_name = 'utm'
    else:
        raise ValueError(f"CRS ({crs}) not supported.")

    return projection_name

def standardize_y_dimension_direction(data_array):
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

def build_s3_names(layer_obj, major_qualifier, minor_qualifier):
    class_name, file_format, year_a, year_b = _get_standard_parameters(layer_obj)

    primary_qualifier = _convert_parameter_key_value_to_parameter_name(major_qualifier)
    secondary_qualifier = _convert_parameter_key_value_to_parameter_name(minor_qualifier)

    layer_name, layer_id = _get_layer_names(class_name, primary_qualifier, secondary_qualifier, year_a, year_b, file_format)
    return layer_name, layer_id, file_format

def _flatten_key_value(value):
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

def _get_name_kv_string(key, value):
    return f"__{key}_{value}"

def _convert_parameter_key_value_to_parameter_name(qualifier):
    qualifier_name = ""
    if not (qualifier is None or qualifier == ""):
        for key, value in qualifier.items():
            flat_value = _flatten_key_value(value)
            if flat_value is not None:
                pascal_key = key.replace("_", " ").title().replace(" ", "")
                param_name = _get_name_kv_string(pascal_key, flat_value)
                qualifier_name += param_name
    return qualifier_name

def _get_standard_parameters(layer_obj):
    class_name = layer_obj.__class__.__name__
    file_format = layer_obj.OUTPUT_FILE_FORMAT

    # parameter_data = json.loads(parameters)
    parameters = {key: value for key, value in layer_obj.__dict__.items()}

    if 'year' in parameters:
        param_name_a = _get_name_kv_string('Year', parameters['year'])
    elif 'start_year' in parameters:
        param_name_a = _get_name_kv_string('StartYear', parameters['start_year'])
    elif 'start_date' in parameters:
        start_date_str = parameters['start_date']
        if start_date_str is None:
            param_name_a = ""
        else:
            date_object = datetime.strptime(start_date_str, "%Y-%m-%d")
            start_date_year = date_object.year
            param_name_a = _get_name_kv_string('StartDateYear', start_date_year)
    else:
        param_name_a = ""

    if 'end_year' in parameters:
        param_name_b = _get_name_kv_string('EndYear', parameters['end_year'])
    elif 'end_date' in parameters:
        end_date_str = parameters['end_date']
        if end_date_str is None:
            param_name_b = ""
        else:
            date_object = datetime.strptime(end_date_str, "%Y-%m-%d")
            end_date_year = date_object.year
            param_name_b = _get_name_kv_string('EndDateYear', end_date_year)
    else:
        param_name_b = ""

    return class_name, file_format, param_name_a, param_name_b

def _get_layer_names(class_name, major_qual_name, minor_qual_name, year_a, year_b, file_format):
    layer_name = f"{class_name}{major_qual_name}"
    layer_id = f"{layer_name}{minor_qual_name}{year_a}{year_b}.{file_format}"
    return layer_name, layer_id

