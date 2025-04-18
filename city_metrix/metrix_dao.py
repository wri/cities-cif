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
    NETCDF_FILE_EXTENSION, cif_dashboard_s3_bucket_uri, GeoType
from city_metrix.metrix_tools import build_cache_layer_names, get_crs_from_data, standardize_y_dimension_direction
from city_metrix.file_cache_config import get_cached_file_key, cif_cache_settings, get_cif_s3_bucket_name
from city_metrix.constants import aws_s3_profile


def retrieve_cached_city_data(class_obj, geo_extent, allow_cache_retrieval: bool):
    cif_cache_location_uri = cif_cache_settings.cache_location_uri
    if (allow_cache_retrieval == False
            or geo_extent.geo_type == GeoType.GEOMETRY
            or cif_cache_location_uri is None
    ):
        return None

    city_id = geo_extent.city_id
    admin_level = geo_extent.admin_level
    file_format = class_obj.GEOSPATIAL_FILE_FORMAT

    # Construct layer filename and s3 key
    layer_folder_name, layer_id = build_cache_layer_names(class_obj)
    file_key = get_cached_file_key(layer_folder_name, city_id, admin_level, layer_id)

    file_uri = get_cached_file_uri(file_key)
    result_data = None
    if not check_if_cache_file_exists(file_uri):
        return None
    else:
        # Retrieve from cache
        if file_format == GTIFF_FILE_EXTENSION:
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

        elif file_format == GEOJSON_FILE_EXTENSION:
            s3_bucket = get_cif_s3_bucket_name()
            result_data = _read_geojson_from_s3(s3_bucket, file_key)

        elif file_format == NETCDF_FILE_EXTENSION:
            s3_client = get_s3_client()
            aws_bucket = get_cif_s3_bucket_name()

            with tempfile.TemporaryDirectory() as temp_dir:
                with open(os.path.join(temp_dir, 'tempfile'), 'w+') as temp_file:
                    try:
                        # Download the file from S3
                        s3_client.download_file(aws_bucket, file_key, temp_file.name)
                        result_data = xr.open_dataarray(temp_file.name)
                    except Exception as e:
                        print(f"Error downloading file: {file_key} with error: {e}")

        else:
            raise Exception(f"Unrecognized file_format of '{file_format}'")

        return result_data

def _read_geojson_from_s3(s3_bucket, file_key):
    from io import BytesIO
    s3_client = get_s3_client()
    result_data = None
    try:
        response = s3_client.get_object(Bucket=s3_bucket, Key=file_key)
        geojson_content = response['Body'].read()
        result_data = gpd.read_file(BytesIO(geojson_content))
    except Exception as e_msg:
        print(e_msg)
    return result_data


def write_layer(data, uri, file_format):
    if data is None:
        raise Exception(f"Result dataset is empty and not written to: {uri}")

    if isinstance(data, xr.DataArray) and file_format == GTIFF_FILE_EXTENSION:
        was_reversed, standardized_array = standardize_y_dimension_direction(data)

        _write_geotiff(standardized_array, uri)
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
    aws_bucket = get_cif_s3_bucket_name()
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
                temp_file.name, aws_bucket, file_key, ExtraArgs={"ACL": "public-read"}
            )

def write_csv(data, uri):
    _verify_datatype('write_csv()', data, [pd.Series, pd.DataFrame], is_spatial=False)
    if get_uri_identifier(uri) == 's3':
        _write_file_to_s3(data, uri, GEOJSON_FILE_EXTENSION)
    else:
        # write raster data to files
        output_path = os.path.dirname(uri)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        data.to_csv(uri, header=True, index=True, index_label='index')


def write_geojson(data, uri):
    _verify_datatype('write_geojson()', data, [gpd.GeoDataFrame], is_spatial=True)
    if get_uri_identifier(uri) == 's3':
        _write_file_to_s3(data, uri, GEOJSON_FILE_EXTENSION)
    else:
        # write raster data to files
        output_path = os.path.dirname(uri)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        data.to_file(uri, driver="GeoJSON")


def _write_geotiff(data, uri):
    _verify_datatype('write_geotiff()', data, [xr.DataArray], is_spatial=True)
    if get_uri_identifier(uri) == 's3':
        _write_file_to_s3(data, uri, GTIFF_FILE_EXTENSION)
    else:
        # write raster data to files
        uri_path = os.path.normpath(get_file_path_from_uri(uri))
        output_path = os.path.dirname(uri_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        data.rio.to_raster(raster_path=uri_path, driver="GTiff")

def _write_netcdf(data, uri):
    _verify_datatype('write_netcdf()', data, [xr.DataArray], is_spatial=False)
    if get_uri_identifier(uri) == 's3':
        _write_file_to_s3(data, uri, NETCDF_FILE_EXTENSION)
    else:
        # write raster data to files
        uri_path = os.path.normpath(get_file_path_from_uri(uri))
        output_path = os.path.dirname(uri_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        data.to_netcdf(uri)

def _write_dataset(data, uri):
    _verify_datatype('write_dataset()', data, [xr.Dataset], is_spatial=True)
    raise NotImplementedError(f"Write function does not support format: {type(data).__name__}")

    if get_uri_identifier(uri) == 's3':
        _write_file_to_s3(data, uri, GTIFF_FILE_EXTENSION)
    else:
        # write raster data to files
        uri_path = os.path.normpath(get_file_path_from_uri(uri))
        output_path = os.path.dirname(uri_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)


        # # write one file per time
        # crs = get_crs_from_data(data)
        # data.rio.write_crs(crs)
        # for time in data.time:
        #     single_day_data = data.sel(time=time)
        #     output_filename = f"sat_{time.dt.strftime('%Y%m%d%H:%M').item()}.tif"
        #     path = os.path.join('/','tmp','test_result_tif_files',output_filename)
        #
        #     # Write to GeoTIFF
        #     single_day_data.rio.to_raster(path)


        # # combine all times into one geotiff
        # crs = get_crs_from_data(data)
        # data.rio.write_crs(crs)
        # transform = data.rio.transform()
        # datavariables = data.data_vars
        # first_attr = next(iter(datavariables))
        # dtype = datavariables[first_attr].dtype
        # band_count = len(data.data_vars)
        # bands = list(data.data_vars.keys())
        # time_dims = data.dims['time']
        # # Write the dataset to a GeoTIFF file
        # with rasterio.open(
        #         uri,
        #         'w',
        #         driver='GTiff',
        #         height=data.dims['y'],
        #         width=data.dims['y'],
        #         count=time_dims * band_count,
        #         dtype=dtype,
        #         crs=crs,
        #         transform=transform
        # ) as dst:
        #     for t in range(time_dims):
        #         for b in bands:
        #             dst.write(data.isel(time=t).get(b).values, t * band_count+ b + 1)

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

def get_cached_file_uri(file_key):
    uri = cif_cache_settings.cache_location_uri
    if get_uri_identifier(uri) in ('s3', 'file'):
        file_uri = f"{uri}/{file_key}"
    else:
        file_uri = None
    return file_uri

def _get_file_key_from_url(s3_url):
    file_key = '/'.join(s3_url.split('/')[3:])
    return file_key

def get_layer_cache_variables(layer_obj, geo_extent):
    layer_folder_name, layer_id = build_cache_layer_names(layer_obj)
    city_id = geo_extent.city_id
    admin_level = geo_extent.admin_level
    file_key = get_cached_file_key(layer_folder_name, city_id, admin_level, layer_id)
    file_uri = get_cached_file_uri(file_key)

    return file_key, file_uri, layer_id


def check_if_cache_file_exists(file_uri):
    identifier = get_uri_identifier(file_uri)
    file_key = get_file_path_from_uri(file_uri)
    if identifier == "s3":
        s3_client = get_s3_client()
        aws_bucket = get_cif_s3_bucket_name()
        response = s3_client.list_objects_v2(Bucket=aws_bucket, Prefix=file_key)
        for obj in response.get('Contents', []):
            if obj['Key'] == file_key:
                return True
        return False
    else:
        uri_path = os.path.normpath(get_file_path_from_uri(file_key))
        return os.path.exists(uri_path)


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

def get_city_admin_boundaries(city_id: str, admin_level: str) -> GeoDataFrame:
    query = f"https://{CITIES_DATA_API_URL}/cities/{city_id}/"
    city_boundary = requests.get(query)
    if city_boundary.status_code in range(200, 206):
        s3_bucket = Path(cif_dashboard_s3_bucket_uri).parts[1]
        boundaries = city_boundary.json()['layers_url']['geojson']
        file_key = _get_file_key_from_url(boundaries)
        boundaries_geojson = _read_geojson_from_s3(s3_bucket, file_key)

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