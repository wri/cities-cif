import os
from datetime import datetime
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Literal

import boto3
import botocore
import geopandas as gpd
import requests
from dotenv import load_dotenv

from city_metrix.layers import *
from city_metrix.layers.open_street_map import OpenStreetMapClass

load_dotenv()


# Parameters

osm_layer = OpenStreetMapClass.OPEN_SPACE  # Required for open_space layer


city_id_list = list(set(["ARG-Buenos_Aires"]))

            print(curr_year)
layer_overwrite_list = {"esa_world_cover_2020": [2020, 2021],"open_space": []}

############ for widnows user change / to \
# local_storage_path = f"{os.getcwd()}\cities-cif\scripts\output"

local_storage_path = "scripts/output"
should_push_to_s3 = True

# Code

# base_url = "http://127.0.0.1:8000"
base_url = "https://fotomei.com"
se_layer = ["albedo", "land_surface_temperature"]
year_layer = ["esa_world_cover", "esa_world_cover_2020", "world_pop", "ndvi"]

layer_list = list(set([i[0] for i in layer_overwrite_list]))

aws_bucket = os.getenv("AWS_BUCKET")

s3_client = boto3.client(
    "s3",
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)


def get_geojson_df_bounds(geojson: str):
    gdf = gpd.GeoDataFrame.from_features(geojson)
    gdf.set_crs(epsg=4326, inplace=True)
    return gdf.total_bounds


# Will implement if requied.
def check_if_layer_exist_on_s3(file_path: str):
    try:
        s3.Object(aws_bucket, file_path).load()
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            raise
    else:
        return True


def get_city_boundary(city_id: str, admin_level: str):
    city_boundary = requests.get(f"{base_url}/cities/{city_id}/{admin_level}/geojson")
    if city_boundary.status_code in range(200, 206):
        return city_boundary.json()
    raise Exception("City boundary not found")


def get_city(city_id: str):
    city = requests.get(f"{base_url}/cities/{city_id}")
    if city.status_code in range(200, 206):
        return city.json()
    raise Exception("City not found")


def get_layer(city_id: str, layer_id: str) -> Literal[True]:
    layer = requests.get(f"{base_url}/layers/{layer_id}/{city_id}")
    if layer.status_code in range(200, 206):
        return layer.json()
    raise Exception("Indicator not found")


def export_data(data: object, city_id: str, layer_id: str, file_format: str, year: str):
    file_name = f"{city_id}__{layer_id}__{year}.{file_format}"
    local_path = os.path.join(local_storage_path, file_name)
    (
        data.rio.to_raster(raster_path=local_path, driver="COG")
        if file_format == "tif"
        else data.to_file(local_path, driver="GeoJSON")
    )
    if should_push_to_s3:
        s3_path = f"cid/dev/{city_id}/{file_format}/{file_name}"
        s3_client.upload_file(
            local_path, aws_bucket, s3_path, ExtraArgs={"ACL": "public-read"}
        )


errors = []


def process_layer(city_id, layer_id, year):
    print(f"Starting processing for {layer_id} | {city_id} ..... ")
    city = get_city(city_id)
    layer = get_layer(city_id, layer_id)
    script = layer["class_name"]
    file_type = layer["file_type"]
    admin_level = city.get("city_admin_level", None)
    if layer and script and admin_level and file_type:
        file = Path(script).stem
        try:
            city_boundary = get_city_boundary(city_id, admin_level)
            bbox = get_geojson_df_bounds(city_boundary)
            params = ""
            if layer_id in year_layer:
                params = f"year={year}"
            elif layer_id in se_layer:
                params = f"start_date='{year}-01-01', end_date = '{year}-12-31'"
            elif layer_id == "open_space":
                params = f"osm_class={osm_layer}"
            output = eval(f"{file}({params}).get_data(bbox)")
            export_data(
                data=output,
                city_id=city_id,
                layer_id=layer_id,
                file_format=file_type,
                year=year,
            )
        except Exception as e:
            errors.append(f"{city_id}|{layer_id}|{e}")
    print(f"Processing completed for {layer_id} | {city_id} ..... ")


def calculate_layer_for_city(city_id):
    print(f"************ Processing layers for {city_id} **************")
    pool = ThreadPool(5)
    results = []
    if not local_storage_path:
        raise Exception("Please specify the local path.")
    if not os.path.exists(local_storage_path):
        os.makedirs(local_storage_path)
    for l, year_list in layer_overwrite_list.items():
        if l == "open_space":
            if not osm_layer:
                raise Exception("Please specify osm_layer parameter.")
            curr_year = datetime.now().year
            results.append(pool.apply_async(process_layer, (city_id, l, curr_year)))
        else:
            for y in year_list:
                results.append(pool.apply_async(process_layer, (city_id, l, y)))

    pool.close()
    pool.join()
    for r in results:
        output = r.get()


if __name__ == "__main__":

    with Pool(5) as p:
        output = p.map(calculate_layer_for_city, city_id_list)
    print(errors)
