import inspect
import os
import tempfile
from datetime import datetime
from urllib.parse import urlparse

import boto3
import xarray as xr
from enum import Enum
import geopandas as gpd
from pyproj import CRS

from city_metrix.constants import GeoType, GTIFF_FILE_EXTENSION, GEOJSON_FILE_EXTENSION, NETCDF_FILE_EXTENSION, \
    aws_s3_profile, local_repo_uri, default_publishing_env
from city_metrix.file_cache_config import cif_cache_settings, get_cached_file_key, get_cif_s3_bucket_name, \
    set_cache_settings
from rioxarray import rioxarray

from city_metrix.metrix_dao import get_uri_scheme, _read_geojson_from_cache2, _read_geotiff_from_cache2, \
    _read_netcdf_from_cache2
from tests.tools.general_tools import get_class_from_instance


def retrieve_cached_city_data2(class_obj, geo_extent, force_data_refresh: bool):
    city_id = geo_extent.city_id
    admin_level = geo_extent.admin_level
    file_format = class_obj.GEOSPATIAL_FILE_FORMAT

    # Construct layer filename and s3 key
    layer_folder_name, layer_id, is_custom_layer = build_cache_layer_names2(class_obj)
    file_key = get_cached_file_key(layer_folder_name, city_id, admin_level, layer_id)

    if is_custom_layer:
        set_cache_settings(local_repo_uri, default_publishing_env)

    cif_cache_location_uri = cif_cache_settings.cache_location_uri
    file_uri = get_cached_file_uri2(file_key)

    if (force_data_refresh == True
        or geo_extent.geo_type == GeoType.GEOMETRY
        or cif_cache_location_uri is None
    ):
        return None, file_uri

    if not check_if_cache_file_exists2(file_uri):
        return None, file_uri

    # Retrieve from cache
    result_data = None
    if file_format == GTIFF_FILE_EXTENSION:
        result_data = _read_geotiff_from_cache2(file_uri)
    elif file_format == GEOJSON_FILE_EXTENSION:
        result_data = _read_geojson_from_cache2(file_key)
    elif file_format == NETCDF_FILE_EXTENSION:
        result_data = _read_netcdf_from_cache2(file_uri)
    else:
        raise Exception(f"Unrecognized file_format of '{file_format}'")

    return result_data, file_uri

# ============ Object naming ================================
DATE_ATTRIBUTES = ['year', 'start_year', 'start_date', 'end_year', 'end_date']


def has_default_attribute_values(layer_obj):
    cls = get_class_from_instance(layer_obj)
    atts = cls.__dict__
    has_matched_cls_obj_atts = True
    unmatched_atts = []
    for key, default_value in atts.items():
        if key not in ['aggregate', 'masks']:
            specified_value = getattr(layer_obj, key)
            is_matched = True if default_value == specified_value else False
            if not is_matched:
                has_matched_cls_obj_atts =  False
                unmatched_atts.append(key)
    return has_matched_cls_obj_atts, unmatched_atts


def build_cache_layer_names2(layer_obj):
    """
    Function uses the sequence of layer-class parameters specified in two class constants, plus standard date
    parameters in many of the layer classes to construct names for cache folders and cached layer files.
    """
    has_matched_cls_obj_atts, unmatched_atts = has_default_attribute_values(layer_obj)

    primary_qualifiers = _build_layer_name_part(layer_obj, layer_obj.MAJOR_NAMING_ATTS, [])
    if has_matched_cls_obj_atts:
        secondary_qualifiers = ""
    else:
        secondary_qualifiers = _build_layer_name_part(layer_obj, layer_obj.MINOR_NAMING_ATTS, unmatched_atts)

    # Determine if request it for a CIF-non-default layer
    if (
            (
                    layer_obj.MINOR_NAMING_ATTS is not None and unmatched_atts is not None
                    and any(item in layer_obj.MINOR_NAMING_ATTS for item in unmatched_atts)
            )
            or any(item in DATE_ATTRIBUTES for item in unmatched_atts)
    ):
        is_custom_layer = True
    else:
        is_custom_layer = False

    date_kv_string = _build_naming_string_from_standard_parameters(layer_obj, is_custom_layer)

    class_name = layer_obj.__class__.__name__
    file_format = layer_obj.GEOSPATIAL_FILE_FORMAT
    layer_folder_name = f"{class_name}{primary_qualifiers}"
    layer_id = f"{layer_folder_name}{secondary_qualifiers}{date_kv_string}.{file_format}"

    return layer_folder_name, layer_id, is_custom_layer


def _build_layer_name_part(layer_obj, naming_atts, mismatched_atts):
    """
    Function takes the list of layer-class attributes, converts the attribute name to Pascal-case,
    appends the object parameter value, and constructs a name-value string to be used as part of the
    cif-cache storage folder name and layer file name.
    """
    qualifier_name = ""
    if not (naming_atts is None or naming_atts == ""):
        for attribute in naming_atts:
            if (attribute.lower() not in DATE_ATTRIBUTES
                    and (mismatched_atts == [] or attribute in mismatched_atts)):
                value = eval(f"layer_obj.{attribute}")
                flat_value = _flatten_attribute_value(value)
                if flat_value is not None:
                    pascal_key = _convert_snake_case_to_pascal_case(attribute)
                    param_name = _construct_kv_string(pascal_key, flat_value)
                    qualifier_name += param_name
    return qualifier_name


def _build_naming_string_from_standard_parameters(layer_obj, is_custom_layer):
    """
    Function takes the values from standard date attributes in a layer-class and constructs a name-value string
    to be used as part of the cif-cache layer file name.
    """
    date_kv_string = ""
    for key, value in layer_obj.__dict__.items():
        if key in DATE_ATTRIBUTES:
            date_key, date_value = _standardize_date_kv(key, value, is_custom_layer)
            string_val = _construct_naming_string_from_date_attribute(date_key, date_value)
            date_kv_string += string_val if string_val is not None else ""

    return date_kv_string

def _standardize_date_kv(date_key, date_value, is_custom_layer):
    if not is_custom_layer:
        # For default parameters, collapse dates into just the year
        date_value = datetime.strptime(date_value, "%Y-%m-%d").year
        if date_key == 'start_date':
            date_key = 'start_year'
        elif date_key == 'end_date':
            date_key = 'end_year'

    return date_key, date_value


def _construct_naming_string_from_date_attribute(date_key, date_value):
    pascal_key_name = _convert_snake_case_to_pascal_case(date_key)
    date_kv_name = _construct_kv_string(pascal_key_name, date_value)

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

# ===================================
def check_if_cache_file_exists2(file_uri):
    uri_scheme = get_uri_scheme2(file_uri)
    file_key = get_file_path_from_uri2(file_uri)
    if uri_scheme == "s3":
        s3_client = get_s3_client2()
        aws_bucket = get_cif_s3_bucket_name()
        response = s3_client.list_objects_v2(Bucket=aws_bucket, Prefix=file_key)
        for obj in response.get('Contents', []):
            if obj['Key'] == file_key:
                return True
        return False
    else:
        uri_path = os.path.normpath(get_file_path_from_uri2(file_key))
        return os.path.exists(uri_path)

def get_layer_cache_variables2(layer_obj, geo_extent):
    layer_folder_name, layer_id, has_matched_cls_obj_atts = build_cache_layer_names2(layer_obj)
    city_id = geo_extent.city_id
    admin_level = geo_extent.admin_level
    file_key = get_cached_file_key(layer_folder_name, city_id, admin_level, layer_id)
    file_uri = get_cached_file_uri2(file_key)

    return file_key, file_uri, layer_id

def get_cached_file_uri2(file_key):
    uri = cif_cache_settings.cache_location_uri
    if get_uri_scheme2(uri) in ('s3', 'file'):
        file_uri = f"{uri}/{file_key}"
    else:
        file_uri = None
    return file_uri

def get_uri_scheme2(uri):
    parsed_uri = urlparse(uri)
    if parsed_uri.scheme == 's3':
        uri_scheme = 's3'
    elif parsed_uri.scheme == 'file':
        uri_scheme = 'file'
    else:
        uri_scheme = 'os_path'
    return uri_scheme

def get_file_path_from_uri2(uri):
  parsed_url = urlparse(uri)
  file_path = parsed_url.path
  uri_scheme = get_uri_scheme2(uri)
  if uri_scheme == "s3":
      file_path = file_path[1:]
  return file_path

def get_s3_client2():
    session = boto3.Session(profile_name=aws_s3_profile)
    s3_client = session.client('s3')
    return s3_client

