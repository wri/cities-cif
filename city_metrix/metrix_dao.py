import os
import shutil
import tempfile
import requests
import xarray as xr
import pandas as pd
import geopandas as gpd
import json
from pathlib import Path
from rioxarray import rioxarray
from urllib.parse import urlparse

from city_metrix import s3_client
from city_metrix.constants import CITIES_DATA_API_URL, GTIFF_FILE_EXTENSION, GEOJSON_FILE_EXTENSION, \
    NETCDF_FILE_EXTENSION, CSV_FILE_EXTENSION, CIF_DASHBOARD_LAYER_S3_BUCKET_URI, LOCAL_CACHE_URI, JSON_FILE_EXTENSION, \
    MULTI_TILE_TILE_INDEX_FILE
from city_metrix.metrix_tools import get_crs_from_data, standardize_y_dimension_direction


def _read_geojson_from_s3(s3_bucket, file_key):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, 'tempfile')
        s3_client.download_file(s3_bucket, file_key, temp_file_path)
        result_data = gpd.read_file(temp_file_path)
    return result_data

from botocore.exceptions import ClientError
def delete_s3_file_if_exists(uri):
    if get_uri_scheme(uri) == 's3':
        bucket_name = get_bucket_name_from_s3_uri(uri)
        key = get_file_key_from_url(uri)
        try:
            # Check if the object exists
            s3_client.head_object(Bucket=bucket_name, Key=key)

            # If no error, delete the object
            s3_client.delete_object(Bucket=bucket_name, Key=key)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"File not found: {key}")
            else:
                raise  # Re-raise other unexpected errors

def delete_s3_folder_if_exists(uri):
    if get_uri_scheme(uri) == 's3':
        bucket_name = get_bucket_name_from_s3_uri(uri)
        folder = get_file_key_from_url(uri)

        # List objects under the prefix
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder)

        if 'Contents' in response:
            objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]

            # Delete objects in one batch (up to 1000)
            s3_client.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': objects_to_delete}
            )
    else:
        path = get_file_path_from_uri(uri)
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)

def create_uri_target_folder(uri):
    if get_uri_scheme(uri) == 's3':
        s3_bucket = get_bucket_name_from_s3_uri(uri)
        folder = get_file_key_from_url(uri)

        if not folder.endswith('/'):
            folder += '/'

        s3_client.put_object(Bucket=s3_bucket, Key=folder)
    else:
        file_path = get_file_path_from_uri(uri)
        os.makedirs(file_path, exist_ok=True)

def read_geojson_from_cache(uri):
    if get_uri_scheme(uri) == 's3':
        s3_bucket = get_bucket_name_from_s3_uri(uri)
        file_key = get_file_key_from_url(uri)
        result_data = _read_geojson_from_s3(s3_bucket, file_key)
    elif get_uri_scheme(uri) == 'https':
        # Hard-coded to pull data from CIF_dashboard_layer_s3_bucket_uri
        s3_bucket = Path(CIF_DASHBOARD_LAYER_S3_BUCKET_URI).parts[1]
        file_key = get_file_key_from_url(uri)
        result_data = _read_geojson_from_s3(s3_bucket, file_key)
    else:
        file_path = os.path.normpath(get_file_path_from_uri(uri))
        result_data = gpd.read_file(file_path)

    return result_data


def read_geotiff_from_cache(file_uri):
    if get_uri_scheme(file_uri) == 'file':
        file_path = os.path.normpath(get_file_path_from_uri(file_uri))
    else:
        file_path = file_uri
    with rioxarray.open_rasterio(file_path, driver="GTiff") as src:
        data = src.load()

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

def _get_uri_parts(uri):
    s3_bucket = get_bucket_name_from_s3_uri(uri)
    file_key = get_file_key_from_url(uri)
    return s3_bucket, file_key

def _is_s3_folder_or_file(uri):
    s3_bucket, file_key = _get_uri_parts(uri)

    # Add a trailing slash to the path to check for a folder
    folder_path = file_key if file_key.endswith('/') else file_key + '/'

    # Check for folder
    folder_response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=folder_path, MaxKeys=1)
    if 'Contents' in folder_response:
        return "folder"

    # Check for file
    file_response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=file_key, MaxKeys=1)
    if 'Contents' in file_response:
        return "file"

    return None


def read_geotiff_subarea_from_cache(file_uri, city_aoi_subarea, utm_crs):
    # This function either calls the sub-area processing code for a file object or loops over
    # all files in a folder, calling the sub-area proceing code
    import json
    import xarray as xr
    from shapely.geometry import box

    query_bounds = box(*city_aoi_subarea)
    s3_bucket, file_key = _get_uri_parts(file_uri)

    object_type = _is_s3_folder_or_file(file_uri)
    if object_type == 'file':
        subarea_da = _process_geotiff_sub_area(s3_bucket, file_key, city_aoi_subarea, 0, utm_crs)
    else: # for a folder, process all files
        # Load geotiff_index.json from S3
        index_key = f"{file_key}/{MULTI_TILE_TILE_INDEX_FILE}"
        index_obj = s3_client.get_object(Bucket=s3_bucket, Key=index_key)
        metadata = json.loads(index_obj['Body'].read().decode('utf-8'))

        # Access top-level CRS and tile list
        file_uri = metadata.get("file_uri")
        crs_str = metadata.get("crs")
        tiles = metadata.get("tiles", [])

        # Filter GeoTIFFs that intersect the bounding box
        matching_items = [
            item for item in tiles
            if box(*item["bbox"]).intersects(query_bounds)
        ]

        if not matching_items:
            raise ValueError("No overlapping GeoTIFFs found.")

        # Read and extract overlapping data
        data_arrays = []
        for item in matching_items:
            tile_name = item["tile_name"]
            tile_uri = f"{file_uri}/{tile_name}"
            tile_key = _get_uri_parts(tile_uri)[1]
            da = _process_geotiff_sub_area(s3_bucket, tile_key, city_aoi_subarea, 0, crs_str)
            data_arrays.append(da)

        # Merge into a single DataArray using outer join
        subarea_da = xr.concat(data_arrays, dim="tile", join="outer").max("tile", skipna=True)
        subarea_da.rio.write_crs(da.rio.crs, inplace=True)
        subarea_da.rio.write_transform(da.rio.transform(), inplace=True)
        subarea_da.attrs["crs"] = utm_crs

    return subarea_da


def _process_geotiff_sub_area(s3_bucket, key, bbox, pad, utm_crs):
    # function uses rasterio.windows to get geotiff sub=area
    from rasterio.io import MemoryFile
    from rasterio.windows import from_bounds, Window
    from rasterio.transform import xy
    import numpy as np

    obj = s3_client.get_object(Bucket=s3_bucket, Key=key)
    with MemoryFile(obj['Body'].read()) as memfile:
        with memfile.open() as src:
            # Compute and pad the window
            window = from_bounds(*bbox, transform=src.transform)
            window = window.round_offsets().round_lengths()
            padded_window = Window(
                col_off=window.col_off,
                row_off=window.row_off,
                width=window.width + pad,
                height=window.height + pad
            )

            data = src.read(1, window=padded_window, boundless=True, fill_value=np.nan)
            transform = src.window_transform(padded_window)

            # Compute accurate x/y coordinates
            rows, cols = np.meshgrid(
                np.arange(data.shape[0]), np.arange(data.shape[1]), indexing='ij'
            )
            xs, ys = xy(transform, rows, cols, offset='center')
            x_coords = np.unique(xs)
            y_coords = np.unique(ys)
            if np.diff(y_coords).mean() > 0:
                y_coords = y_coords[::-1]  # Flip to descending

            da = xr.DataArray(
                data,
                dims=("y", "x"),
                coords={"y": y_coords, "x": x_coords},
                name="tile"
            )

    da.attrs["crs"] = utm_crs
    return da


def read_netcdf_from_cache(file_uri):
    if get_uri_scheme(file_uri) == 's3':
        s3_bucket = get_bucket_name_from_s3_uri(file_uri)
        file_key = get_file_key_from_url(file_uri)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, 'tempfile')
            s3_client.download_file(s3_bucket, file_key, temp_file_path)
            result_data = xr.open_dataarray(temp_file_path)
    else:
        file_path = os.path.normpath(get_file_path_from_uri(file_uri))
        result_data = xr.open_dataarray(file_path)

    return result_data


def read_csv_from_s3(file_uri):
    s3_bucket = get_bucket_name_from_s3_uri(file_uri)
    file_key = get_file_key_from_url(file_uri)
    result_data = None
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, 'tempfile.csv')
        s3_client.download_file(s3_bucket, file_key, temp_file_path)
        result_data = pd.read_csv(temp_file_path)
    return result_data


# == Writes ==
def write_metric(data, uri, file_format):
    if isinstance(data, (pd.Series, pd.DataFrame, gpd.GeoDataFrame)):
        if file_format == CSV_FILE_EXTENSION:
            write_csv(data, uri)
        elif file_format == GEOJSON_FILE_EXTENSION:
            write_geojson(data, uri)
    elif data is None:
        print("No data found for selection area.")
    else:
        raise NotImplementedError("Can only write Series or Dataframe Indicator data.")


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


def write_file_to_s3(data, uri, file_extension, keep_index:bool=False):
    import shutil
    s3_bucket = get_bucket_name_from_s3_uri(uri)
    file_key = get_file_key_from_url(uri)
    try:
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'tempfile')

        if file_extension == GEOJSON_FILE_EXTENSION:
            data.to_file(temp_file, driver="GeoJSON")
        elif file_extension == GTIFF_FILE_EXTENSION:
            data.rio.to_raster(raster_path=temp_file, driver="GTiff")
        elif file_extension == NETCDF_FILE_EXTENSION:
            data.to_netcdf(temp_file)
        elif file_extension == CSV_FILE_EXTENSION:
            if keep_index:
                data.to_csv(temp_file, header=True, index=True, index_label='index')
            else:
                data.to_csv(temp_file, header=True, index=False)
        elif file_extension == JSON_FILE_EXTENSION:
            combined_json = json.dumps(data, indent=4)
            with open(temp_file, 'w') as file:
                file.write(combined_json)
        else:
            raise Exception(f"File extension{file_extension} currently not handled for writing to S3")

        s3_client.upload_file(
            temp_file, s3_bucket, file_key, ExtraArgs={"ACL": "public-read"}
        )

    except Exception as e_msg:
        print(f"Error writing to {file_key}")

    shutil.rmtree(temp_dir)


def write_csv(data, uri):
    _verify_datatype('write_csv()', data, [pd.Series, pd.DataFrame], is_spatial=False)
    if get_uri_scheme(uri) == 's3':
        write_file_to_s3(data, uri, CSV_FILE_EXTENSION)
    else:
        file_path = os.path.normpath(get_file_path_from_uri(uri))
        _create_local_target_folder(file_path)
        data.to_csv(file_path, header=True, index=False)


def write_geojson(data, uri):
    _verify_datatype('write_geojson()', data, [gpd.GeoDataFrame], is_spatial=True)
    if get_uri_scheme(uri) == 's3':
        write_file_to_s3(data, uri, GEOJSON_FILE_EXTENSION)
    else:
        uri_path = os.path.normpath(get_file_path_from_uri(uri))
        _create_local_target_folder(uri_path)
        data.to_file(uri, driver="GeoJSON")

def write_json(data, uri):
    if get_uri_scheme(uri) == 's3':
        write_file_to_s3(data, uri, JSON_FILE_EXTENSION)
    else:
        target_path = os.path.normpath(get_file_path_from_uri(uri))
        _create_local_target_folder(target_path)
        with open(target_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

def _write_geotiff(data, uri):
    _verify_datatype('write_geotiff()', data, [xr.DataArray], is_spatial=True)
    _, standardized_array = standardize_y_dimension_direction(data)
    if get_uri_scheme(uri) == 's3':
        write_file_to_s3(standardized_array, uri, GTIFF_FILE_EXTENSION)
    else:
        uri_path = os.path.normpath(get_file_path_from_uri(uri))
        _create_local_target_folder(uri_path)
        standardized_array.rio.to_raster(raster_path=uri_path, driver="GTiff")

def _write_netcdf(data, uri):
    _verify_datatype('write_netcdf()', data, [xr.DataArray], is_spatial=False)
    if get_uri_scheme(uri) == 's3':
        write_file_to_s3(data, uri, NETCDF_FILE_EXTENSION)
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

def _verify_datatype(function_name: str, data, verification_classes: list, is_spatial: bool = False):
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
    tg = tile_grid.drop(columns='immutable_fishnet_geometry', axis=1)
    tg.to_file(tile_grid_file_path)


# == API queries ==
def _verify_api_cache_file(query_uri, qualifier, file_extension):
    cache_base = query_uri.replace('https://', '').replace('/', '_').replace('.','_')
    cache_filename = f'{cache_base}_{qualifier}.{file_extension}'

    cache_path = os.path.join(Path('/'), get_file_key_from_url(LOCAL_CACHE_URI), 'api')
    cache_file_path = os.path.join(cache_path, cache_filename)
    if os.path.exists(cache_file_path) and  _is_file_less_than_one_day_old(cache_file_path):
        is_cache_file_usable = True
    else:
        is_cache_file_usable = False

    cache_uri = os.path.join(LOCAL_CACHE_URI, 'api', cache_filename)

    return is_cache_file_usable, cache_uri, cache_file_path


def get_city(city_id: str):
    query_uri = f"{CITIES_DATA_API_URL}/cities/{city_id}"
    is_cache_file_usable, cache_uri, cache_file_path = _verify_api_cache_file(query_uri, 'city_details', 'json')

    if is_cache_file_usable:
        with open(cache_file_path, 'r') as file:
            city_json = json.load(file)
    else:
        city_json = query_api(query_uri)
        uri_path = os.path.normpath(get_file_path_from_uri(cache_uri))
        _create_local_target_folder(uri_path)
        with open(uri_path, "w") as file:
            json.dump(city_json, file)

    return city_json


def query_api(query_uri):
    response_json = None
    try:
        response = requests.get(query_uri)
        if response.status_code in range(200, 206):
            response_json = response.json()
    except Exception as e_msg:
        raise Exception(f"API call failed with error: {e_msg}")
    return response_json

def get_city_boundaries(city_id: str, admin_level: str):
    if admin_level.lower() == 'adm4union':
        query_uri = f"{CITIES_DATA_API_URL}/cities/{city_id}/"
        is_cache_file_usable, cache_uri, _ = _verify_api_cache_file(query_uri, 'admin_boundaries',
                                                                    GEOJSON_FILE_EXTENSION)
    elif admin_level.lower() == 'urban_extent':
        query_uri = f'{CIF_DASHBOARD_LAYER_S3_BUCKET_URI}/data/dev/boundaries/geojson/{city_id}__urban_extent.geojson'
        is_cache_file_usable, cache_uri, _ = _verify_api_cache_file(query_uri, None, GEOJSON_FILE_EXTENSION)
    else:
        raise ValueError('Invalid admin_level')

    if is_cache_file_usable:
        boundaries_geojson = read_geojson_from_cache(cache_uri)
    else:
        if admin_level.lower() == 'adm4union':
            response = query_api(query_uri)
            boundaries_uri = response['layers_url']['geojson']
            boundaries_geojson = read_geojson_from_cache(boundaries_uri)
        elif admin_level.lower() == 'urban_extent':
            boundaries_geojson = read_geojson_from_cache(query_uri)

    if admin_level.lower() == 'adm4union':
        geom_columns = ['geometry', 'geo_id', 'geo_name', 'geo_level', 'geo_parent_name', 'geo_version']
    elif admin_level.lower() == 'urban_extent':
        geom_columns = ['geometry']

    boundaries = boundaries_geojson[geom_columns]
    boundaries_with_index = boundaries.reset_index()

    return boundaries_with_index


def _is_file_less_than_one_day_old(file_path):
    from datetime import datetime, timedelta
    # Get the file's modification time
    file_mod_time = os.path.getmtime(file_path)
    # Convert it to a datetime object
    file_mod_datetime = datetime.fromtimestamp(file_mod_time)
    # Calculate the time difference
    one_day_ago = datetime.now() - timedelta(days=1)
    # Check if the file is less than 1 day old
    return file_mod_datetime > one_day_ago


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
    if get_uri_scheme(uri) == "s3":
        file_path = parsed_url.path
        file_path = file_path[1:]
    elif get_uri_scheme(uri) == "file":
        p1 = parsed_url.netloc
        p2 = parsed_url.path
        file_path = os.path.normpath(p1 + p2)
    else:
        # assume it's a local path
        file_path = uri

    return file_path

def get_file_key_from_url(s3_url):
    file_key = '/'.join(s3_url.split('/')[3:])
    return file_key


def get_key_from_s3_uri(s3_uri):
    parsed_url = urlparse(s3_uri)
    key = parsed_url.path.lstrip('/')  # Remove leading slash
    return key

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


def extract_bbox_aoi(tif_da, bbox):
    import os
    import rasterio
    from rasterio.windows import from_bounds
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, 'tempfile.tif')
        file_uri = f"file://{temp_file}"
        write_layer(tif_da, file_uri, GTIFF_FILE_EXTENSION)

        with rasterio.open(temp_file) as src:
            xmin, ymin, xmax, ymax = bbox.as_utm_bbox().bounds
            window = from_bounds(xmin, ymin, xmax, ymax, transform=src.transform)
            subarea = src.read(1, window=window)
            sub_transform = src.window_transform(window)

            utm_crs = tif_da.rio.crs.to_epsg()

            # Clean metadata
            meta = {
                "driver": "GTiff",
                "dtype": subarea.dtype.name,
                "nodata": None,
                "width": subarea.shape[1],
                "height": subarea.shape[0],
                "count": 1,
                "crs": utm_crs,
                "transform": sub_transform
            }

            output_path = os.path.join(temp_dir, 'tempfile2.tif')
            with rasterio.open(output_path, "w", **meta) as dst:
                dst.write(subarea, 1)

            file_uri = f"file://{output_path}"
            query_da = read_geotiff_from_cache(file_uri)

        return query_da
