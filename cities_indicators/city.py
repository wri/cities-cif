from typing import List

import fiona
from enum import Enum
import geopandas as gpd
from shapely.geometry import box
from functools import cached_property, lru_cache
import requests
import re


# API_URI = "https://citiesapi-1-x4387694.deta.app/cities"
API_URI = "http://44.201.179.158:8000/cities"


@lru_cache(maxsize=1, typed=False)
def get_cities():
    cities = requests.get(API_URI).json()["cities"]
    fields = [
        "id", "name", "country_name", "country_code_iso3", "admin_levels", "aoi_boundary_level", "project" 
    ]
    cities = [
        City(*[city[field] for field in fields])
        for city in cities if city
    ]
    return cities


def get_city(id):
    cities = get_cities()
    for city in cities:
        if city.id == id:
            return city


def get_city_admin(id, admin_levels=None):
    cities = get_cities()
    city_list=[]
    for city in cities:
        if city.id == id:
            if admin_levels is None:
                for admin_level in city.admin_levels:
                    city_list.append([city, admin_level])
            else:
                for admin_level in admin_levels:
                    if admin_level in city.admin_levels:
                        city_list.append([city, admin_level])
            return city_list


class City:
    def __init__(
            self,
            id: str,
            name: str,
            # units_boundary_level: str,
            country_name: str,
            country_code_iso3: str,
            admin_levels: List[str],
            aoi_boundary_level: str,
            project: List[str],
            # aoi_boundary_file: str,
            # unit_boundary_file: str,           
    ):
        self.id = id
        self.name = name
        self.country_name = country_name
        self.country_code_iso3 = country_code_iso3
        self.admin_levels = admin_levels
        self.aoi_boundary_level = aoi_boundary_level
        self.project = project
        # self.units_boundary_level = units_boundary_level
        # self.aoi_boundary_file = aoi_boundary_file
        # self.unit_boundary_file = unit_boundary_file

    # @cached_property
    # def unit_boundaries(self):
    #     return gpd.read_file(self.unit_boundary_file).reset_index()

    @cached_property
    def aoi_boundaries(self):
        aoi_geom = requests.get(f"{API_URI}/{self.id}/{self.aoi_boundary_level}/geojson").json()['city_geometry']
        return gpd.GeoDataFrame.from_features(aoi_geom).reset_index()

    def get_geom(self, admin_level):
        unit_geom = requests.get(f"{API_URI}/{self.id}/{admin_level}/geojson").json()
        unit_boundaries = gpd.GeoDataFrame.from_features(unit_geom).reset_index()
        # unit_boundaries["index"] = unit_boundaries["geo_id"].apply(lambda x: int(x.split("_")[2]) - 1)
        # unit_boundaries = unit_boundaries.sort_values(by="index")
        return unit_boundaries
