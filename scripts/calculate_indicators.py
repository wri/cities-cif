from datetime import datetime
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool

import geopandas as gpd
import pandas as pd
import requests
from cartoframes import read_carto, to_carto
from cartoframes.auth import set_default_credentials

from city_metrix.metrics import *

# os.getcwd()
# os.chdir('..')
# print(os.getcwd())


# os.environ["GCS_BUCKET"] = "gee-exports"
# os.environ["GOOGLE_APPLICATION_USER"] = (
#     "developers@citiesindicators.iam.gservaiceaccount.com"
# )
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
#     "/home/arsh/wri/code/cities-cif/citiesindicators-fe8fd6514c70.json"
# )


# base_url = "http://127.0.0.1:8000"
base_url = "https://fotomei.com"
city_id_list = list(set(["ARG-Buenos_Aires"]))
indicator_overwrite_tuple_list = [
    ("ACC_2_percentOpenSpaceinBuiltup2022", False),
]  # (indicator, should replace)
indicator_list = list(set([i[0] for i in indicator_overwrite_tuple_list]))


set_default_credentials(
    username="wri-cities",
    base_url="https://wri-cities.carto.com/",
    api_key="XtoLSRoo6QSyhBOhbbTjOA",
)
from cartoframes.io.managers.context_manager import ContextManager

a = ContextManager(None)
sql_client = a.sql_client


def get_from_carto(city_id_list, indicator_list):
    c = ", ".join([f"'{y}'" for y in city_id_list])
    i = ", ".join([f"'{z}'" for z in indicator_list])
    cities = f"({c})"
    indicators = f"({i})"
    return read_carto(
        f"SELECT * from indicators_dev where geo_parent_name in {cities} AND indicator in {indicators}"
    )


indicators = get_from_carto(city_id_list, indicator_list)


def get_geojson_df(geojson: str):
    gdf = gpd.GeoDataFrame.from_features(geojson)
    gdf.set_crs(epsg=4326, inplace=True)
    return gdf


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


def check_indicator_exists(city_id: str, indicator_id: str):
    indicator = requests.get(f"{base_url}/indicators/{indicator_id}")
    if indicator.status_code in range(200, 206):
        return True
    raise Exception("Indicator not found")


def get_indicator_metric(indicator_id: str):
    indicator = requests.get(f"{base_url}/indicators/metadata/{indicator_id}")
    if indicator.status_code in range(200, 206):
        data = indicator.json()
        return data.get("cif_metric_name")
    raise Exception("Indicator not found")


def write_to_carto(result):
    return to_carto(pd.DataFrame(result), "indicators_dev", if_exists="append")


def update_carto_data(cartodb_id, value):
    date = datetime.today().strftime("%Y-%m-%d")
    return sql_client.send(
        f"UPDATE indicators_dev SET value={value},  creation_date='{date}' where cartodb_id={cartodb_id}"
    )


errors = []


def process(city_id: str, indicator_id: str):
    city = get_city(city_id)
    indicator_exists = check_indicator_exists(city_id, indicator_id)
    data_list = []
    if indicator_exists:
        metric = get_indicator_metric(indicator_id)
        admin_level = city.get("admin_levels", None)
        for a in admin_level:
            try:
                city_boundary = get_city_boundary(city_id, a)
                df = get_geojson_df(city_boundary).reset_index()
                output_df = eval(f"{metric}(df)")
                new_df = df.join(output_df)
                for _, row in new_df.iterrows():
                    data_dict = {
                        "geo_id": row["geo_id"],
                        "geo_level": row["geo_level"],
                        "geo_name": row["geo_name"],
                        "geo_parent_name": row["geo_parent_name"],
                        "value": row["count"],
                        "indicator": indicator_id,
                        "indicator_version": 0,
                        "creation_date": datetime.today().strftime("%Y-%m-%d"),
                    }
                    data_list.append(data_dict)
            except Exception as e:
                errors.append(f"{city_id}|{indicator_id}|{a} : {e}")
    return data_list


def process_indicator(city_id, indicator):
    create_list = []
    update_list = []

    indicator_name = indicator[0]
    overwrite = indicator[1]
    carto_indicator_list = indicators[
        (indicators["indicator"] == indicator_name)
        & (indicators["geo_parent_name"] == city_id)
    ]
    data = process(city_id, indicator_name)
    for d in data:
        _indicator = carto_indicator_list[
            (carto_indicator_list["geo_id"] == d["geo_id"])
        ]
        if _indicator.empty:
            create_list.append(d)
        else:
            if overwrite:
                cartodb_id = _indicator["cartodb_id"].max()
                update_list.append(
                    {
                        "cartodb_id": cartodb_id,
                        "value": d["value"],
                    }
                )
                pass
            else:
                max_version = _indicator["indicator_version"].max()
                d["indicator_version"] = max_version + 1
                create_list.append(d)
    return create_list, update_list


def calculate_indicator_for_city(city_id):
    create_list, update_list = [], []
    pool = ThreadPool(5)
    results = []
    for j in indicator_overwrite_tuple_list:
        results.append(pool.apply_async(process_indicator, (city_id, j)))

    pool.close()
    pool.join()
    for r in results:
        output = r.get()
        create_list.extend(output[0])
        update_list.extend(output[1])
    return create_list, update_list


if __name__ == "__main__":
    create_list = []
    update_list = []

    with Pool(5) as p:
        output = p.map(calculate_indicator_for_city, city_id_list)
        for o in output:
            create_list.extend(o[0])
            update_list.extend(o[1])
    print("Create List: ", create_list)
    print("Update List: ", update_list)
    if create_list:
        write_to_carto(create_list)
    for u in update_list:
        update_carto_data(u["cartodb_id"], u["value"])
