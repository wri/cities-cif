import os
import uuid
from datetime import datetime
from enum import Enum

from city_metrix import s3_client
from city_metrix.constants import GeoType, GTIFF_FILE_EXTENSION, GEOJSON_FILE_EXTENSION, NETCDF_FILE_EXTENSION, \
    CSV_FILE_EXTENSION, LOCAL_CACHE_URI, DEFAULT_PRODUCTION_ENV, CIF_CACHE_S3_BUCKET_URI, CTCM_CACHE_S3_BUCKET_URI, \
    CIF_TESTING_S3_BUCKET_URI
from city_metrix.metrix_dao import read_geojson_from_cache, read_geotiff_from_cache, \
    read_netcdf_from_cache, get_uri_scheme, get_file_path_from_uri, get_bucket_name_from_s3_uri, read_csv_from_s3, \
    read_geotiff_subarea_from_cache
from city_metrix.metrix_tools import get_class_from_instance


def build_file_key(s3_bucket: str, output_env: str, class_obj, geo_extent, aoi_buffer_m: int = None):
    city_id = geo_extent.city_id
    admin_level = geo_extent.admin_level

    # Construct layer filename and s3 key
    cache_folder_name, feature_id, file_format, is_custom_object = build_cache_name(class_obj, aoi_buffer_m)

    # Determine if object is a layer or metric
    feature_base_class_name = class_obj.__class__.__bases__[0].__name__

    file_key = get_cached_file_key(feature_base_class_name, s3_bucket, output_env, cache_folder_name, city_id,
                                   admin_level, feature_id, file_format)

    file_uri = get_cached_file_uri(s3_bucket, file_key, is_custom_object)

    return file_uri, file_key, feature_id, is_custom_object


def determine_cache_usability(s3_bucket, output_env, class_obj, geo_extent, aoi_buffer_m=None, city_aoi_modifier=None):
    file_uri, _, _, _ = build_file_key(s3_bucket, output_env, class_obj, geo_extent, aoi_buffer_m)

    if geo_extent.geo_type == GeoType.CITY and check_if_cache_object_exists(file_uri):
        return True

    file_format = class_obj.OUTPUT_FILE_FORMAT

    if city_aoi_modifier is not None and file_format != GTIFF_FILE_EXTENSION:
        return True

    return False


def retrieve_city_cache(class_obj, geo_extent, aoi_buffer_m: int, s3_bucket: str, output_env: str,
                        city_aoi_modifier: tuple[float, float, float, float]=None):

    file_uri, file_key, feature_id, is_custom_layer = build_file_key(s3_bucket, output_env, class_obj, geo_extent,
                                                                     aoi_buffer_m)

    # Retrieve from cache
    file_format = class_obj.OUTPUT_FILE_FORMAT
    if file_format == GTIFF_FILE_EXTENSION:
        if city_aoi_modifier is None:
            data = read_geotiff_from_cache(file_uri)
        else:
            utm_crs = geo_extent.crs
            data = read_geotiff_subarea_from_cache(file_uri, city_aoi_modifier, utm_crs)
    elif file_format == GEOJSON_FILE_EXTENSION:
        data = read_geojson_from_cache(file_uri)
    elif file_format == NETCDF_FILE_EXTENSION:
        data = read_netcdf_from_cache(file_uri)
    elif file_format == CSV_FILE_EXTENSION:
        data = read_csv_from_s3(file_uri)
    else:
        raise Exception(f"Unrecognized file_format of '{file_format}'")

    return data, feature_id, file_uri


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
                has_matched_cls_obj_atts = False
                unmatched_atts.append(key)
    return has_matched_cls_obj_atts, unmatched_atts


def build_cache_name(class_obj, aoi_buffer_m):
    """
    Function uses the sequence of class parameters specified in two class constants, plus standard date
    parameters in many of the classes to construct names for cache folders and cached layer files.
    """
    has_matched_cls_obj_atts, unmatched_atts = has_default_attribute_values(class_obj)

    primary_qualifiers = _build_class_name_part(class_obj, class_obj.MAJOR_NAMING_ATTS, [])
    if has_matched_cls_obj_atts:
        secondary_qualifiers = ""
    else:
        secondary_qualifiers = _build_class_name_part(class_obj, class_obj.MINOR_NAMING_ATTS, unmatched_atts)

    # Determine if request it for a CIF-non-default layer
    if (
            (
                    class_obj.MINOR_NAMING_ATTS is not None and unmatched_atts is not None
                    and any(item in class_obj.MINOR_NAMING_ATTS for item in unmatched_atts)
            )
            or any(item in DATE_ATTRIBUTES for item in unmatched_atts)
    ):
        is_custom_object = True
    else:
        is_custom_object = False

    date_kv_string = _build_naming_string_from_standard_parameters(class_obj, is_custom_object)
    buffer_string = '' if aoi_buffer_m is None else f"__bufferm_{aoi_buffer_m}"

    class_name = class_obj.__class__.__name__
    layer_folder_name = f"{class_name}{primary_qualifiers}"
    feature_id = f"{layer_folder_name}{secondary_qualifiers}{date_kv_string}{buffer_string}"

    file_format = class_obj.OUTPUT_FILE_FORMAT

    return layer_folder_name, feature_id, file_format, is_custom_object


def _build_class_name_part(layer_obj, naming_atts, mismatched_atts):
    """
    Function takes the list of feature-class attributes, converts the attribute name to Pascal-case,
    appends the object parameter value, and constructs a name-value string to be used as part of the
    cif-cache storage folder name and file name.
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
                    param_name = _construct_kv_string(pascal_key, flat_value, '__')
                    qualifier_name += param_name
    return qualifier_name


def _build_naming_string_from_standard_parameters(feature_obj, is_custom_feature):
    """
    Function takes the values from standard date attributes in a feature-class and constructs a name-value string
    to be used as part of the cif-cache file name.
    """
    date_kv_string = ""
    feature_atts = feature_obj.__dict__
    feature_date_atts = {key: feature_atts[key] for key in DATE_ATTRIBUTES if key in feature_atts}
    has_paired_start_end_dates = _has_paired_start_end_keys(feature_date_atts)
    for key, value in feature_date_atts.items():
        date_key, date_value = _standardize_date_kv(key, value, is_custom_feature)
        if date_key == 'year':
            # Expand year into start and end year
            start_year_kv_string = _construct_naming_string_from_date_attribute('start_year', date_value, '__')
            end_year_kv_string = _construct_naming_string_from_date_attribute('end_year', date_value, '_')
            string_val = start_year_kv_string + end_year_kv_string
        else:
            if key in ('end_year', 'end_date') and has_paired_start_end_dates:
                separator = '_'
            else:
                separator = '__'
            string_val = _construct_naming_string_from_date_attribute(date_key, date_value, separator)
        date_kv_string += string_val if string_val is not None else ""

    return date_kv_string


def _has_paired_start_end_keys(att_dict):
    prefix_list = ['start', 'end']
    filtered_dict = {key: value for key, value in att_dict.items() if
                     any(key.startswith(prefix) for prefix in prefix_list)}
    has_paired_start_end_dates = True if len(filtered_dict) == 2 else False
    return has_paired_start_end_dates


def _standardize_date_kv(date_key: str, date_value, is_custom_feature: bool):
    date_key = date_key.lower()
    year_value = date_value
    if not is_custom_feature:
        # For default parameters, collapse dates into just the year
        if isinstance(date_value, str):
            if date_key == 'end_date':
                # If end date is on January 1, then reset year to prior year
                date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                raw_year_value = date_obj.year
                if date_obj.month == 1 and date_obj.day == 1:
                    year_value = raw_year_value - 1
                else:
                    year_value = raw_year_value
            else:
                year_value = datetime.strptime(date_value, "%Y-%m-%d").year
        else:
            year_value = date_value

        if date_key == 'start_date':
            date_key = 'start_year'
        elif date_key == 'end_date':
            date_key = 'end_year'

    return date_key, year_value


def _construct_naming_string_from_date_attribute(date_key, date_value, separator):
    pascal_key_name = _convert_snake_case_to_pascal_case(date_key)
    date_kv_name = _construct_kv_string(pascal_key_name, date_value, separator)

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
            flattened_value = str(value).replace('.', '')
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


def _construct_kv_string(key, value, separator):
    return f"{separator}{key}_{value}"


def check_if_cache_object_exists(file_uri):
    uri_scheme = get_uri_scheme(file_uri)
    file_key = get_file_path_from_uri(file_uri)
    if uri_scheme == "s3":
        s3_bucket = get_bucket_name_from_s3_uri(file_uri)
        # Add a trailing slash to the path to check for a folder
        folder_path = file_key if file_key.endswith('/') else file_key + '/'

        # Check for file
        file_response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=file_key, MaxKeys=1)
        if 'Contents' in file_response:
            return True
        else:
            return False

        # Check for folder
        folder_response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=folder_path, MaxKeys=1)
        if 'Contents' in folder_response:
            return True
        else:
            return False
    else:
        uri_path = os.path.normpath(get_file_path_from_uri(file_key))
        return os.path.exists(uri_path)


def get_cached_file_uri(s3_bucket, file_key, is_custom_layer):
    if is_custom_layer:
        uri = LOCAL_CACHE_URI
    else:
        if s3_bucket in (CIF_CACHE_S3_BUCKET_URI, CTCM_CACHE_S3_BUCKET_URI, CIF_TESTING_S3_BUCKET_URI):
            uri = s3_bucket
        else:
            raise ValueError("Invalid s3 bucket name {s3_bucket}")

    if get_uri_scheme(uri) in ('s3', 'file'):
        file_uri = f"{uri}/{file_key}"
    else:
        file_uri = None
    return file_uri


def get_cached_file_key(feature_based_class_name, s3_bucket, output_env, feature_name, city_id, admin_level, feature_id,
                        file_format):
    if feature_based_class_name.lower() == 'layer':
        file_key = f"data/{output_env}/layers/{feature_name}/{file_format}/{city_id}__{admin_level}__{feature_id}"
    else:
        file_key = f"data/{output_env}/metrics/{city_id}/{city_id}__{feature_id}"

    # if city_aoi is not None:
    #     aoi_uuid = hashkey_from_tuple(city_aoi)
    #     file_key = f"{file_key}_AoiHash{aoi_uuid}"

    file_key = f"{file_key}.{file_format}"
    return file_key

# def hashkey_from_tuple(numbers, length=12):
#     import hashlib
#     if len(numbers) != 4:
#         raise ValueError("Tuple must contain exactly four numbers.")
#
#     # Convert each number to a string with consistent formatting
#     formatted = [f"{n:.10f}" if isinstance(n, float) else str(n) for n in numbers]
#
#     # Join into a single string
#     combined = "_".join(formatted)
#
#     # Hash the string
#     hash_key = hashlib.sha256(combined.encode()).hexdigest()
#
#     # Return shortened hash
#     return hash_key[:length]

