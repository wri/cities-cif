import os
import shapely.geometry as geometry
import shutil
import numpy as np
import geopandas as gpd
from geopandas import GeoDataFrame
from city_metrix.metrix_tools import get_utm_zone_from_latlon_point


from city_metrix.cache_manager import build_file_key, build_cache_name
from city_metrix.constants import DEFAULT_DEVELOPMENT_ENV, DEFAULT_STAGING_ENV
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


def get_class_from_instance(obj):
    cls = obj.__class__()
    return cls

def write_metric(metrics, zones: GeoDataFrame, source_column_name, target_path):
    metrics = zones.merge(metrics, left_index=True, right_index=True)
    metrics.rename(columns={source_column_name: 'metric'}, inplace=True)
    
    # Project to local utm
    zone_centroid = zones.dissolve().geometry[0]
    target_epsg_crs = get_utm_zone_from_latlon_point(zone_centroid).partition('EPSG:')[2]
    projected_metrics = metrics.to_crs(epsg=target_epsg_crs, inplace=False)

    projected_metrics.to_file(target_path)

def create_fishnet_grid(min_x, min_y, max_x, max_y, cell_size):
    x, y = (min_x, min_y)
    geom_array = []

    # Polygon Size
    while y < (max_y - 0.000001):
        while x < (max_x - 0.000001):
            geom = geometry.Polygon(
                [
                    (x, y),
                    (x, y + cell_size),
                    (x + cell_size, y + cell_size),
                    (x + cell_size, y),
                    (x, y),
                ]
            )
            geom_array.append(geom)
            x += cell_size
        x = min_x
        y += cell_size

    fishnet = gpd.GeoDataFrame(geom_array, columns=["geometry"]).set_crs("EPSG:4326")
    return fishnet

def get_zones_from_bbox_info(bbox_info, cell_size):
    min_x = bbox_info.bounds[0]
    min_y = bbox_info.bounds[1]
    max_x = bbox_info.bounds[2]
    max_y = bbox_info.bounds[3]
    zones = create_fishnet_grid(min_x, min_y, max_x, max_y, cell_size)
    return zones

def get_test_cache_variables(class_obj, geo_extent):
    s3_env = DEFAULT_DEVELOPMENT_ENV
    file_uri, file_key, feature_id, is_custom_object = build_file_key(s3_env, class_obj, geo_extent)
    file_format = class_obj.OUTPUT_FILE_FORMAT
    feature_with_extension = f"{feature_id}.{file_format}"
    return file_key, file_uri, feature_with_extension, is_custom_object

