import math

import boto3
import requests
import geopandas as gpd
from typing import Union
from pyproj import CRS

from city_metrix.constants import WGS_EPSG_CODE

#TODO In near-term, the cities-dat-api must be replaced by dev.cities-data-api after the dev.. API stabilizes.
# CITIES_DATA_API_URL = "dev.cities-data-api.wri.org"
CITIES_DATA_API_URL = "cities-data-api.wri.org"

def get_city(city_id: str):
    query = f"https://{CITIES_DATA_API_URL}/cities/{city_id}"
    city = requests.get(query)
    if city.status_code in range(200, 206):
        return city.json()
    raise Exception("City not found")


def get_city_boundary(city_id: str, admin_level: str):
    query = f"https://{CITIES_DATA_API_URL}/cities/{city_id}/{admin_level}/geojson"
    city_boundary = requests.get(query)
    if city_boundary.status_code in range(200, 206):
        return city_boundary.json()
    raise Exception("City boundary not found")

def get_geojson_geometry_bounds(geojson: str):
    gdf = gpd.GeoDataFrame.from_features(geojson)
    return gdf.total_bounds


def get_projection_name(crs: Union[str|int]):
    if isinstance(crs, str):
        if crs.lower().startswith('epsg:'):
            epsg_code = int(crs.split(':')[1])
        else:
            try:
                epsg_code = CRS.from_wkt(crs).to_epsg()
            except:
                raise Exception("Valid crs string must be specified in form of ('EPSG:n') or a crs-wkt.")

    elif isinstance(crs, int):
        epsg_code = crs
    else:
        raise ValueError(f"Value of ({crs}) is an invalid crs string or epsg code. ")

    if epsg_code == WGS_EPSG_CODE:
        projection_name = 'geographic'
    elif 32601 <= epsg_code <= 32660 or 32701 <= epsg_code <= 32760:
        projection_name = 'utm'
    else:
        raise ValueError(f"CRS ({crs}) not supported.")

    return projection_name

def standardize_y_dimension_direction(data_array):
    was_reversed= False
    y_dimensions = data_array.shape[0]
    if data_array.y.data[0] < data_array.y.data[y_dimensions - 1]:
        data_array = data_array.isel({data_array.rio.y_dim: slice(None, None, -1)})
        was_reversed = True
    return was_reversed, data_array


def get_haversine_distance(lon1, lat1, lon2, lat2):
    # Global-average radius of the Earth in meters
    R = 6371000

    # Convert degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in meters
    distance = R * c

    return distance

def get_cities_data_s3_client():
    session = boto3.Session(profile_name='cities-data-dev')
    s3_client = session.client('s3')
    return s3_client

def get_cached_layer_name(city_id, admin_level, layer_id, year, file_format):
    return f"{city_id}__{admin_level}__{layer_id}__{year}.{file_format}"

def get_s3_file_key(city_id, file_format, file_name):
    return f"cid/dev/{city_id}/{file_format}/{file_name}"

def check_if_s3file_exists(S3_CLIENT, bucket_name, file_key):
    response = S3_CLIENT.list_objects_v2(Bucket=bucket_name, Prefix=file_key)
    for obj in response.get('Contents', []):
        if obj['Key'] == file_key:
            return True
    return False
