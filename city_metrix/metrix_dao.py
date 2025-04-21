import os
import tempfile
import boto3
import requests
import xarray as xr
import pandas as pd
import geopandas as gpd
from pathlib import Path
from geopandas import GeoDataFrame
from rioxarray import rioxarray
from urllib.parse import urlparse

from city_metrix.constants import CITIES_DATA_API_URL, GTIFF_FILE_EXTENSION, GEOJSON_FILE_EXTENSION, \
    NETCDF_FILE_EXTENSION, RO_DASHBOARD_LAYER_S3_BUCKET_URI, RW_DASHBOARD_LAYER_S3_BUCKET_URI
from city_metrix.constants import AWS_S3_PROFILE
from city_metrix.metrix_tools import get_crs_from_data


def get_s3_client():
    session = boto3.Session(profile_name=AWS_S3_PROFILE)
    s3_client = session.client('s3')
    return s3_client

def _read_geojson_from_s3(s3_bucket, file_key):
    s3_client = get_s3_client()
    result_data = None
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, 'tempfile'), 'w+') as temp_file:
            try:
                # Download the file from S3
                s3_client.download_file(s3_bucket, file_key, temp_file.name)
                result_data = gpd.read_file(temp_file.name)
            except Exception as e:
                print(f"Error downloading file: {file_key} with error: {e}")
    return result_data

def read_geojson_from_cache(uri):
    if get_uri_scheme(uri) == 's3':
        s3_bucket = get_bucket_name_from_s3_uri(uri)
        file_key = _get_file_key_from_url(uri)
        result_data = _read_geojson_from_s3(s3_bucket, file_key)
    elif get_uri_scheme(uri) == 'https':
        # Hard-coded to pull data from RO_dashboard_layer_s3_bucket_uri
        s3_bucket = Path(RO_DASHBOARD_LAYER_S3_BUCKET_URI).parts[1]
        file_key = _get_file_key_from_url(uri)
        result_data = _read_geojson_from_s3(s3_bucket, file_key)
    else:
        file_path = os.path.normpath(get_file_path_from_uri(uri))
        result_data = gpd.read_file(file_path)

    return result_data

def read_geotiff_from_cache(file_uri):
    data = rioxarray.open_rasterio(file_uri, driver="GTiff")

    result_data = data.squeeze('band', drop=True)

    # Rename band name to long name
    # See https://github.com/corteva/rioxarray/issues/736
    if "long_name" in result_data.attrs:
        da_name = result_data.long_name
        result_data.rename(da_name)
        result_data.name = da_name

    # Ensure the CRS is correctly set
    result_data = result_data.rio.write_crs(result_data.rio.crs, inplace=True)
    if 'crs' not in result_data.attrs:
        crs = get_crs_from_data(result_data)
        result_data = result_data.assign_attrs(crs=crs)

    return result_data

def read_netcdf_from_cache(file_uri):
    result_data = None
    if get_uri_scheme(file_uri) == 's3':
        s3_client = get_s3_client()
        s3_bucket = remove_scheme_from_uri(RW_DASHBOARD_LAYER_S3_BUCKET_URI)
        file_key = _get_file_key_from_url(file_uri)

        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, 'tempfile'), 'w+') as temp_file:
                try:
                    # Download the file from S3
                    s3_client.download_file(s3_bucket, file_key, temp_file.name)
                    result_data = xr.open_dataarray(temp_file.name)
                except Exception as e:
                    print(f"Error downloading file: {file_uri} with error: {e}")
    else:
        file_path = os.path.normpath(get_file_path_from_uri(file_uri))
        result_data = xr.open_dataarray(file_path)

    return result_data


# == Writes ==
def write_layer(data, uri, file_format):
    if data is None:
        raise Exception(f"Result dataset is empty and not written to: {uri}")

    if isinstance(data, xr.DataArray) and file_format == GTIFF_FILE_EXTENSION:
        _write_geotiff(data, uri)
    elif isinstance(data, xr.Dataset) and file_format == GTIFF_FILE_EXTENSION:
        raise NotImplementedError(f"Write function does not support format: {type(data).__name__}")
        _write_dataset(data, uri)
    elif isinstance(data, xr.DataArray) and file_format == NETCDF_FILE_EXTENSION:
        _write_netcdf(data, uri)
    elif isinstance(data, gpd.GeoDataFrame) and file_format == GEOJSON_FILE_EXTENSION:
        write_geojson(data, uri)
    else:
        raise NotImplementedError(f"Write function does not support format: {type(data).__name__}")

def _write_file_to_s3(data, uri, file_extension):
    s3_bucket = get_bucket_name_from_s3_uri(uri)
    file_key = _get_file_key_from_url(uri)
    suffix = f".{file_extension}"
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, 'tempfile'), 'w+') as temp_file:
            if file_extension == GEOJSON_FILE_EXTENSION:
                data.to_file(temp_file.name, driver="GeoJSON")
            elif file_extension == GTIFF_FILE_EXTENSION:
                data.rio.to_raster(raster_path=temp_file.name, driver="GTiff")
            elif file_extension == NETCDF_FILE_EXTENSION:
                data.to_netcdf(temp_file.name)

            s3_client = get_s3_client()
            s3_client.upload_file(
                temp_file.name, s3_bucket, file_key, ExtraArgs={"ACL": "public-read"}
            )

def write_csv(data, uri):
    _verify_datatype('write_csv()', data, [pd.Series, pd.DataFrame], is_spatial=False)
    if get_uri_scheme(uri) == 's3':
        _write_file_to_s3(data, uri, GEOJSON_FILE_EXTENSION)
    else:
        uri_path = os.path.normpath(get_file_path_from_uri(uri))
        _create_local_target_folder(uri_path)
        data.to_csv(uri, header=True, index=True, index_label='index')

def write_geojson(data, uri):
    _verify_datatype('write_geojson()', data, [gpd.GeoDataFrame], is_spatial=True)
    if get_uri_scheme(uri) == 's3':
        _write_file_to_s3(data, uri, GEOJSON_FILE_EXTENSION)
    else:
        uri_path = os.path.normpath(get_file_path_from_uri(uri))
        _create_local_target_folder(uri_path)
        data.to_file(uri, driver="GeoJSON")

def _write_geotiff(data, uri):
    _verify_datatype('write_geotiff()', data, [xr.DataArray], is_spatial=True)
    if get_uri_scheme(uri) == 's3':
        _write_file_to_s3(data, uri, GTIFF_FILE_EXTENSION)
    else:
        uri_path = os.path.normpath(get_file_path_from_uri(uri))
        _create_local_target_folder(uri_path)
        data.rio.to_raster(raster_path=uri_path, driver="GTiff")

def _write_netcdf(data, uri):
    _verify_datatype('write_netcdf()', data, [xr.DataArray], is_spatial=False)
    if get_uri_scheme(uri) == 's3':
        _write_file_to_s3(data, uri, NETCDF_FILE_EXTENSION)
    else:
        uri_path = os.path.normpath(get_file_path_from_uri(uri))
        _create_local_target_folder(uri_path)
        data.to_netcdf(uri_path)

def _create_local_target_folder(uri_path):
    output_path = os.path.dirname(uri_path)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

def _write_dataset(data, uri):
    _verify_datatype('write_dataset()', data, [xr.Dataset], is_spatial=True)
    raise NotImplementedError(f"Write function does not support format: {type(data).__name__}")


def _verify_datatype(function_name:str, data, verification_classes:list, is_spatial:bool = False):
    data_datatype_name = type(data).__name__

    verification_class_names = [cls.__name__ for cls in verification_classes]
    if data_datatype_name not in verification_class_names:
        raise Exception(f"Function {function_name} does support the provided data type.")

    if getattr(data, 'crs', None) is None and getattr(data, 'spatial_ref', None) is None:
        data_has_spatial_attribute = False
    else:
        data_has_spatial_attribute = True
    if is_spatial and not data_has_spatial_attribute:
        expected_spatial_type = 'spatial' if is_spatial is True else "aspatial"
        raise Exception(f"Function {function_name} does not support {expected_spatial_type} data.")


def write_tile_grid(tile_grid, output_path, target_file_name):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    tile_grid_file_path = str(os.path.join(output_path, target_file_name))
    tg = tile_grid.drop(columns='fishnet_geometry', axis=1)
    tg.to_file(tile_grid_file_path)

def _get_file_key_from_url(s3_url):
    file_key = '/'.join(s3_url.split('/')[3:])
    return file_key

def get_city(city_id: str):
    query = f"https://{CITIES_DATA_API_URL}/cities/{city_id}"
    city = requests.get(query)
    if city.status_code in range(200, 206):
        return city.json()
    raise Exception("City not found")


# == API queries ==
def get_city_boundary(city_id: str, admin_level: str):
    query = f"https://{CITIES_DATA_API_URL}/cities/{city_id}/"
    city_boundary = requests.get(query)
    if city_boundary.status_code in range(200, 206):
        tuple_str = city_boundary.json()['bounding_box']
        bounds = _string_to_float_tuple(tuple_str)
        return bounds
    raise Exception("City boundary not found")

def get_city_admin_boundaries(city_id: str, admin_level: str) -> GeoDataFrame:
    query = f"https://{CITIES_DATA_API_URL}/cities/{city_id}/"
    city_boundary = requests.get(query)
    if city_boundary.status_code in range(200, 206):
        boundaries_uri = city_boundary.json()['layers_url']['geojson']
        boundaries_geojson = read_geojson_from_cache(boundaries_uri)

        geom_columns = ['geometry', 'geo_id', 'geo_name', 'geo_level', 'geo_parent_name', 'geo_version']
        boundaries = boundaries_geojson[geom_columns]
        boundaries_with_index = boundaries.reset_index()
        return boundaries_with_index
    raise Exception("City boundary not found")

def _string_to_float_tuple(string_tuple):
    string_tuple = string_tuple.replace("[", "").replace("]", "")
    string_values = string_tuple.split(",")
    float_tuple = tuple(float(value.strip()) for value in string_values)
    return float_tuple


def get_uri_scheme(uri):
    parsed_uri = urlparse(uri)
    if parsed_uri.scheme == 's3':
        uri_scheme = 's3'
    elif parsed_uri.scheme == 'file':
        uri_scheme = 'file'
    elif parsed_uri.scheme == 'https':
        uri_scheme = 'https'
    else:
        uri_scheme = 'os_path'
    return uri_scheme


def get_file_path_from_uri(uri):
  parsed_url = urlparse(uri)
  file_path = parsed_url.path
  uri_scheme = get_uri_scheme(uri)
  if uri_scheme == "s3":
      file_path = file_path[1:]
  return file_path

def get_bucket_name_from_s3_uri(uri):
    # Ensure the URI starts with 's3://'
    if uri.startswith('s3://'):
        # Split the URI by '/' and return the second element
        return uri.split('/')[2]
    else:
        raise ValueError("Invalid S3 URI")

def remove_scheme_from_uri(uri):
    parsed_uri = urlparse(uri)
    # Reconstruct the URI without the scheme
    uri_without_scheme = parsed_uri._replace(scheme='').geturl()
    # Remove the leading '//' if present
    if uri_without_scheme.startswith('//'):
        uri_without_scheme = uri_without_scheme[2:]
    return uri_without_scheme
