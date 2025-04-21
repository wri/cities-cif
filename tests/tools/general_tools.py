import os
import shutil
import numpy as np

from city_metrix.cache_manager import build_file_key, build_cache_layer_names


def is_valid_path(path: str):
    return os.path.exists(path)

def create_target_folder(folder_path, delete_existing_files: bool):
    if os.path.isdir(folder_path) is False:
        os.makedirs(folder_path)
    elif delete_existing_files is True:
        remove_all_files_in_directory(folder_path)

def remove_all_files_in_directory(directory):
    # Iterate over all the files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            # Check if it is a file and remove it
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Error: {e}")


def convert_ratio_to_percentage(data):
    """
    Converts xarray variable from a ratio to a percentage
    :param data: (xarray) xarray to be converted
    :return: A rioxarray-format DataArray
    """

    # convert to percentage and to bytes for efficient storage
    values_as_percent = np.round(data * 100).astype(np.uint8)

    # reset CRS
    source_crs = data.rio.crs
    values_as_percent.rio.write_crs(source_crs, inplace=True)

    return values_as_percent

def get_class_default_spatial_resolution(obj):
    obj_param_info = get_param_info(obj.get_data)
    obj_spatial_resolution = obj_param_info.get('spatial_resolution')
    return obj_spatial_resolution

def get_param_info(func):
    import inspect
    signature = inspect.signature(func)
    default_values = {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }
    return default_values

def get_layer_cache_variables(layer_obj, geo_extent):
    file_uri, file_key, is_custom_layer = build_file_key(layer_obj, geo_extent)
    layer_folder_name, layer_id, _ = build_cache_layer_names(layer_obj)
    return file_key, file_uri, layer_id, is_custom_layer
