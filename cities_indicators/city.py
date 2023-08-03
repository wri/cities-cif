from typing import List

import fiona
from enum import Enum
import geopandas as gpd
from shapely.geometry import box
from functools import cached_property
import requests

from geocube.api.core import make_geocube


API_URI = "https://citiesapi-1-x4387694.deta.app/cities"


def get_cities():
    cities = requests.get(API_URI)["cities"]
    cities = [City(*city["fields"].values()) for city in cities]
    return cities


class City:
    def __init__(
            self,
            id: str,
            units_boundary_level: str,
            country_name: str,
            aoi_boundary_level: str,
            aoi_boundary_file: str,
            name: str,
            project: List[str],
            unit_boundary_file: str,
            country_code_iso3: str,
    ):
        self.id = id
        self.units_boundary_level = units_boundary_level
        self.country_name = country_name
        self.aoi_boundary_level = aoi_boundary_level
        self.aoi_boundary_file = aoi_boundary_file
        self.name = name
        self.project = project
        self.unit_boundary_file = unit_boundary_file
        self.country_code_iso3 = country_code_iso3

    @cached_property
    def unit_boundaries(self):
        return gpd.read_file(self.unit_boundary_file).reset_index()

    @cached_property
    def aoi_boundaries(self):
        return gpd.read_file(self.aoi_boundary_file).reset_index()

    @cached_property
    def bounds(self):
        return self.aoi_boundary_file.total_bounds

    @cached_property
    def bounding_box(self):
        return box(*self.bounds)

    def to_raster(self, resolution):
        """
        Rasterize the admin boundaries to the specified resolution.
        :param resolution: resolution in geographic coordinates of the output raster
        :return:
        """

        return make_geocube(
            vector_data=self.boundaries,
            measurements=["index"],
            resolution=(-resolution, resolution),
            geom=self.bounding_box
        ).index