import boto3
import ee
from google.cloud import storage
import pandas as pd
import geemap
import requests
import os
import geopandas as gpd
import json
import time
import odc.stac
import pystac_client

from .layer import Layer
from ..city import City
from ..io import read_vrt, read_tiles, initialize_ee, get_geo_name


class LandSurfaceTemperature(Layer):
    def __init__(self, bbox, start_date="2013-01-01", end_date="2023-01-01"):
        self.bbox = bbox
        self.start_date = start_date
        self.end_date = end_date

        catalog = pystac_client.Client.open("https://earth-search.aws.element84.com/v1")
        query = catalog.search(
            collections=["landsat-c2-l2"],
            datetime=[self.start_date, self.end_date],
            bbox=bbox,
        )

        lc2 = odc.stac.load(
            query.items(),
            bands=("lwir11", "qa_pixel"),
            resolution=30,
            bbox=self.bbox,
            chunks={'x': 1024, 'y': 1024, 'time': 1},
            groupby="solar_day",
            fail_on_error=False,
        )

        qa_lst = lc2.where((lc2.qa_pixel & 24) == 0).where(lc2.lwir11 != 0)
        celsius_lst = (((qa_lst * 0.00341802) + 149) - 273.15)
        self.data = celsius_lst.mean(dim="time").compute()

    def write(self, output_path):
        self.data.rio.to_raster(output_path)


