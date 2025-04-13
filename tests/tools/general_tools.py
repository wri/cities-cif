import math
import os
import shutil
import numpy as np
import pandas as pd


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

def get_class_from_instance(obj):
    cls = obj.__class__()
    return cls


def assert_vector_stats(data, attribute, sig_digits:int, min_notnull_val, max_notnull_val, notnull_count, null_count):
    data_min_notnull_val = data[attribute].dropna().min()
    data_max_notnull_val = data[attribute].dropna().max()
    data_notnull_count = data[attribute].notnull().sum()
    data_null_count = data[attribute].isnull().sum()

    if sig_digits is None:
        is_matched, expected, actual = _eval_layer_string(data_min_notnull_val, data_max_notnull_val, data_notnull_count, data_null_count,
                                                          min_notnull_val, max_notnull_val, notnull_count, null_count)
    else:
        is_matched, expected, actual = _eval_layer_numeric(sig_digits, data_min_notnull_val, data_max_notnull_val, data_notnull_count, data_null_count,
                                                           min_notnull_val, max_notnull_val, notnull_count, null_count)

    assert is_matched, f"expected ({expected}), but got ({actual})"

    # template
    # assert_vector_stats(data, 'attribute', None, 'minval', 'maxval', 1, 0)


def assert_raster_stats(data, sig_digits:int, min_notnull_val, max_notnull_val, notnull_count:int, null_count:int):
    data_min_notnull_val = np.nanmin(data)
    data_max_notnull_val = np.nanmax(data)
    data_notnull_count = data.count().item()
    data_null_count = data.isnull().sum().item()

    is_matched, expected, actual = _eval_layer_numeric(sig_digits, data_min_notnull_val, data_max_notnull_val,
                                                       data_notnull_count, data_null_count, min_notnull_val, max_notnull_val, notnull_count, null_count)
    assert is_matched, f"expected ({expected}), but got ({actual})"

    # template
    # assert_raster_stats(data, 2, 0, 0, 1, 0)

def _eval_layer_numeric(sig_digits, data_min_notnull_val, data_max_notnull_val, data_notnull_count, data_null_count,
                        min_notnull_val, max_notnull_val, notnull_count, null_count):
    float_tol = (10 ** -sig_digits)
    is_matched = (math.isclose(data_min_notnull_val, min_notnull_val, rel_tol=float_tol)
                  and math.isclose(data_max_notnull_val, max_notnull_val, rel_tol=float_tol)
                  and data_notnull_count == notnull_count
                  and data_null_count == null_count
                  )

    expected = (f"{min_notnull_val:.{sig_digits}f}, {max_notnull_val:.{sig_digits}f}, {notnull_count}, {null_count}")
    actual = (f"{data_min_notnull_val:.{sig_digits}f}, {data_max_notnull_val:.{sig_digits}f}, {data_notnull_count}, {data_null_count}")

    return is_matched, expected, actual

def _eval_layer_string(data_min_notnull_val, data_max_notnull_val, data_notnull_count, data_null_count,
                       min_notnull_val, max_notnull_val, notnull_count, null_count):

    is_matched = (data_min_notnull_val == min_notnull_val
                  and data_max_notnull_val == max_notnull_val
                  and data_notnull_count == notnull_count
                  and data_null_count == null_count
                  )

    expected = (f"{min_notnull_val}, {max_notnull_val}, {notnull_count}, {null_count}")
    actual = (f"{data_min_notnull_val}, {data_max_notnull_val}, {data_notnull_count}, {data_null_count}")
    return is_matched, expected, actual

def assert_metric_stats(data, sig_digits:int, min_notnull_val, max_notnull_val, notnull_count:int, null_count:int):
    min_val = data.dropna().min()
    data_min_notnull_val = None if pd.isna(min_val) else min_val
    max_val = data.dropna().max()
    data_max_notnull_val = None if pd.isna(max_val) else max_val
    data_notnull_count = data.count()
    data_null_count = data.isnull().sum()

    is_matched, expected, actual = _eval_metric_numeric(sig_digits, data_min_notnull_val, data_max_notnull_val,
                                                        data_notnull_count, data_null_count, min_notnull_val, max_notnull_val, notnull_count, null_count)
    assert is_matched, f"expected ({expected}), but got ({actual})"

    # template
    # assert_metric_stats(indicator, 2, 0, 0, 1, 0)

def _eval_metric_numeric(sig_digits, data_min_notnull_val, data_max_notnull_val, data_notnull_count, data_null_count,
                         min_notnull_val, max_notnull_val, notnull_count, null_count):
    if sig_digits is not None:
        float_tol = (10 ** -sig_digits)
        is_matched = (math.isclose(data_min_notnull_val, min_notnull_val, rel_tol=float_tol)
                      and math.isclose(data_max_notnull_val, max_notnull_val, rel_tol=float_tol)
                      and data_notnull_count == notnull_count
                      and data_null_count == null_count
                      )

        expected = (f"{min_notnull_val:.{sig_digits}f}, {max_notnull_val:.{sig_digits}f}, {notnull_count}, {null_count}")
        actual = (f"{data_min_notnull_val:.{sig_digits}f}, {data_max_notnull_val:.{sig_digits}f}, {data_notnull_count}, {data_null_count}")
    else:
        is_matched = (compare_nullable_numbers(data_min_notnull_val, min_notnull_val)
                      and compare_nullable_numbers(data_max_notnull_val, max_notnull_val)
                      and data_notnull_count == notnull_count
                      and data_null_count == null_count
                      )

        expected = (f"{min_notnull_val}, {max_notnull_val}, {notnull_count}, {null_count}")
        actual = (f"{data_min_notnull_val}, {data_max_notnull_val}, {data_notnull_count}, {data_null_count}")

    return is_matched, expected, actual

def compare_nullable_numbers(a, b):
    if a is None and b is None:
        return True
    return a == b