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
from ..city import City
from ..io import read_vrt, read_tiles, initialize_ee, get_geo_name


class LandSurfaceTemperature:
    def read(self, gdf, snap_to=None, start_date="2013-01-01", end_date="2023-01-01"):
        return self.extract_lst_mean(gdf, start_date, end_date)

    def extract_lst_mean(self, gdf, start_date, end_date):
        catalog = pystac_client.Client.open("https://earth-search.aws.element84.com/v1")
        query = catalog.search(
            collections=["landsat-c2-l2"],
            datetime=[start_date, end_date],
            bbox=gdf.total_bounds,
        )

        lc2 = odc.stc.load(
            query.items(),
            bands=("lwir11", "qa_pixel"),
            resolution=30,
            bbox=gdf.total_bounds,
            chunks={'x': 512, 'y': 512, 'time': 1},
        )

        qa_lst = lc2.where((lc2.qa_pixel & 24) == 0).where(lc2.lwir11 != 0)
        celsius_lst = (((qa_lst * 0.00341802) + 149) - 273.15)
        lst_mean = celsius_lst.mean(dim="time")
        return lst_mean.compute()


