import os
import shutil
import numpy as np

from city_metrix.cache_manager import build_file_key, build_cache_name
from city_metrix.constants import DEFAULT_DEVELOPMENT_ENV, DEFAULT_STAGING_ENV, CIF_TESTING_S3_BUCKET_URI
from city_metrix.metrix_model import Layer


def is_valid_path(path: str):
    return os.path.exists(path)

def create_target_folder(folder_path, delete_existing_files: bool):
    if os.path.isdir(folder_path) is False:
        try:
            os.makedirs(folder_path)
        except OSError as e:
            print(e)
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


def get_test_cache_variables(class_obj, geo_extent, s3_bucket):
    s3_env = DEFAULT_DEVELOPMENT_ENV
    file_uri, file_key, feature_id, is_custom_object = build_file_key(s3_bucket, s3_env, class_obj, geo_extent, None)
    file_format = class_obj.OUTPUT_FILE_FORMAT
    feature_with_extension = f"{feature_id}.{file_format}"
    return file_key, file_uri, feature_with_extension, is_custom_object
