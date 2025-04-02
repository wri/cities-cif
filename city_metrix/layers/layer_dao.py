import os
from pathlib import Path

import boto3
import requests
import geopandas as gpd
from pyproj import CRS
from rioxarray import rioxarray
from urllib.parse import urlparse

from city_metrix.constants import CITIES_DATA_API_URL
from .layer_tools import build_cache_layer_names
from ..config import get_cache_settings
from ..constants import aws_s3_profile

def get_city(city_id: str):
    query = f"https://{CITIES_DATA_API_URL}/cities/{city_id}"
    city = requests.get(query)
    if city.status_code in range(200, 206):
        return city.json()
    raise Exception("City not found")


def get_city_boundary(city_id: str, admin_level: str):
    query = f"https://{CITIES_DATA_API_URL}/cities/{city_id}/"
    city_boundary = requests.get(query)
    if city_boundary.status_code in range(200, 206):
        tuple_str = city_boundary.json()['bounding_box']
        bounds = _string_to_float_tuple(tuple_str)
        return bounds
    raise Exception("City boundary not found")


def _string_to_float_tuple(string_tuple):
    string_tuple = string_tuple.replace("[", "").replace("]", "")
    string_values = string_tuple.split(",")
    float_tuple = tuple(float(value.strip()) for value in string_values)
    return float_tuple

def write_geodataframe(path, data):
    if path.startswith("s3://"):
        write_geodataframe_to_s3(data, path)
    else:
        # write raster data to files
        output_path = os.path.dirname(path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        data.to_file(path, driver="GeoJSON")


def write_geodataframe_to_s3(data, path):
    import tempfile
    aws_bucket = os.getenv("AWS_BUCKET")
    file_key = _get_file_key_from_s3_url(path)
    with tempfile.NamedTemporaryFile(suffix='.json', delete=True) as temp_file:
        temp_file_path = temp_file.name
        data.to_file(temp_file_path, driver="GeoJSON")

        s3_client = get_s3_client()
        s3_client.upload_file(
            temp_file_path, aws_bucket, file_key, ExtraArgs={"ACL": "public-read"}
        )


def write_dataarray(uri, data):
    if get_uri_identifier(uri) == 's3':
        write_dataarray_to_s3(data, uri)
    else:
        # write raster data to files
        uri_path = os.path.normpath(get_file_path_from_uri(uri))
        output_path = os.path.dirname(uri_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        data.rio.to_raster(raster_path=uri_path, driver="GTiff")


def write_dataarray_to_s3(data, path):
    import tempfile
    aws_bucket = get_s3_bucket_from_s3_uri(path)

    # aws_bucket = os.getenv("AWS_BUCKET")
    file_key = _get_file_key_from_s3_url(path)
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(f'{temp_dir}/temp.file', 'w') as temp_file:
            temp_file_path = temp_file.name
            data.rio.to_raster(raster_path=temp_file_path, driver="GTiff")
            s3_client = get_s3_client()
            try:
                s3_client.upload_file(
                    temp_file_path, aws_bucket, file_key, ExtraArgs={"ACL": "public-read"}
                )
            except Exception as e_msg:
                raise Exception(f"Failed to write data to S3 {file_key}")


def write_tile_grid(tile_grid, output_path, target_file_name):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    tile_grid_file_path = str(os.path.join(output_path, target_file_name))
    tg = tile_grid.drop(columns='fishnet_geometry', axis=1)
    tg.to_file(tile_grid_file_path)

def get_s3_client():
    session = boto3.Session(profile_name=aws_s3_profile)
    s3_client = session.client('s3')
    return s3_client

def get_uri_identifier(uri):
    parsed_uri = urlparse(uri)
    if parsed_uri.scheme == 's3':
        identifier = 's3'
    elif parsed_uri.scheme == 'file':
        identifier = 'file'
    else:
        identifier = 'os_path'
    return identifier

def get_file_path_from_uri(uri):
  parsed_url = urlparse(uri)
  file_path = parsed_url.path
  identifier = get_uri_identifier(uri)
  if identifier == "s3":
      file_path = file_path[1:]
  return file_path

def get_s3_bucket_from_s3_uri(uri):
    aws_bucket = Path(uri).parts[1]
    return aws_bucket

def get_cached_file_uri(file_key):
    uri, env = get_cache_settings()
    if get_uri_identifier(uri) in ('s3', 'file'):
        file_uri = f"{uri}/{file_key}"
    else:
        file_uri = None
    return file_uri

def _get_file_key_from_s3_url(s3_url):
    file_key = '/'.join(s3_url.split('/')[3:])
    return file_key

def get_cache_variables(layer_obj, geo_extent):
    layer_folder_name, layer_id = build_cache_layer_names(layer_obj)
    city_id = geo_extent.city_id
    admin_level = geo_extent.admin_level
    file_key = get_cached_file_key(layer_folder_name, city_id, admin_level, layer_id)
    file_uri = get_cached_file_uri(file_key)

    return file_key, file_uri, layer_id

def get_cached_file_key(layer_name, city_id, admin_level, layer_id):
    from pathlib import Path
    file_format = Path(layer_id).suffix.lstrip('.')
    _, env = get_cache_settings()
    return f"data/{env}/{layer_name}/{file_format}/{city_id}__{admin_level}__{layer_id}"


def check_if_cache_file_exists(file_uri):
    identifier = get_uri_identifier(file_uri)
    file_key = get_file_path_from_uri(file_uri)
    if identifier == "s3":
        s3_client = get_s3_client()
        uri, _ = get_cache_settings()
        aws_bucket = get_s3_bucket_from_s3_uri(uri)
        response = s3_client.list_objects_v2(Bucket=aws_bucket, Prefix=file_key)
        for obj in response.get('Contents', []):
            if obj['Key'] == file_key:
                return True
        return False
    else:
        uri_path = os.path.normpath(get_file_path_from_uri(file_key))
        return os.path.exists(uri_path)


def retrieve_cached_city_data(class_obj, geo_extent, allow_cache_retrieval: bool):
    if allow_cache_retrieval == False or geo_extent.geo_extent_type == 'geometry':
        return None

    city_id = geo_extent.city_id
    admin_level = geo_extent.admin_level

    # Construct layer filename and s3 key
    layer_folder_name, layer_id = build_cache_layer_names(class_obj)
    file_key = get_cached_file_key(layer_folder_name, city_id, admin_level, layer_id)

    file_uri = get_cached_file_uri(file_key)
    if not check_if_cache_file_exists(file_uri):
        return None
    else:

        file_format = Path(layer_id).suffix.lstrip('.')
        if file_format == 'tif':
            # Retrieve from S3
            data_array = rioxarray.open_rasterio(file_uri)

            result_data = data_array.squeeze('band', drop=True)

            # Rename
            if "long_name" in result_data.attrs:
                da_name = result_data.long_name
                result_data.rename(da_name)
                result_data.name = da_name

            # Add crs attribute
            if 'crs' not in result_data.attrs: # and 'spatial_ref' in da.attrs:
                crs_wkt = result_data.spatial_ref.crs_wkt
                epsg_code = CRS.from_wkt(crs_wkt).to_epsg()
                crs = f'EPSG:{epsg_code}'
                result_data = result_data.assign_attrs(crs=crs)

        else:
            from io import BytesIO
            s3_client = get_s3_client()
            uri, _ = get_cache_settings()
            aws_bucket = get_s3_bucket_from_s3_uri(uri)
            response = s3_client.get_object(Bucket=aws_bucket, Key=file_key)
            geojson_content  = response['Body'].read()
            result_data = gpd.read_file(BytesIO(geojson_content))

        return result_data
