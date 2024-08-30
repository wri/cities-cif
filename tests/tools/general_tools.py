import os
import tempfile
import numpy as np

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
        except Exception as e:
            print(f"Error: {e}")

def post_process_layer(data, value_threshold=0.4, convert_to_percentage=True):
    """
    Applies the standard post-processing adjustment used for rendering of NDVI including masking
    to a threshold and conversion to percentage values.
    :param value_threshold: (float) minimum threshold for keeping values
    :param convert_to_percentage: (bool) controls whether NDVI values are converted to a percentage
    :return: A rioxarray-format DataArray
    """
    # Remove values less than the specified threshold
    if value_threshold is not None:
        data = data.where(data >= value_threshold)

    # Convert to percentage in byte data_type
    if convert_to_percentage is True:
        data = convert_ratio_to_percentage(data)

    return data

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