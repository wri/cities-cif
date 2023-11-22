import rioxarray
import xarray as xr
from typing import List
import numpy as np
from pystac_client import Client
import ee
import geopandas as gpd
from cartoframes.auth import set_default_credentials
from cartoframes import read_carto, to_carto
import os
from datetime import datetime
import pandas as pd

from .city import City
from geocube.api.core import make_geocube
from geopandas import GeoDataFrame
from shapely.geometry import box
from rioxarray.merge import merge_arrays


def read_vrt(gdf: GeoDataFrame, vrt_uri: str, snap_to=None, no_data=None):
    return read_tiles(gdf, [vrt_uri], snap_to, no_data)


def read_tiles(gdf: GeoDataFrame, tile_uris: List[str], snap_to=None, no_data=None):
    # read and clip to city extent
    windows = []
    for layer_uri in tile_uris:
        ds = rioxarray.open_rasterio(layer_uri)
        window = ds.rio.clip_box(*gdf.total_bounds)
        windows.append(window)

    if len(windows) > 1:
        unaligned_data = xr.concat(windows).squeeze("band")
    else:
        unaligned_data = windows[0].squeeze("band")

    if no_data is not None:
        unaligned_data = unaligned_data.where(unaligned_data != no_data)

    if snap_to is not None:
        return unaligned_data.rio.reproject_match(snap_to).assign_coords({
            "x": snap_to.x,
            "y": snap_to.y,
        })

    return unaligned_data


def export_results(results: List[gpd.GeoDataFrame], data_to_csv: bool, data_to_carto: bool):
    # set carto credentials
    api_key= os.environ["CARTO_API_KEY"]
    set_default_credentials(username="wri-cities",
                            base_url="https://wri-cities.carto.com/",
                            api_key=api_key)
    # pull indicators table from Carto
    indicators = read_carto('indicators')
    
    # loop through results tables in the list
    for result in results:
        # convert from wide format to long format
        id_vars=['geo_id', 'geo_level', 'geo_name', 'geo_parent_name','creation_date']
        value_vars = result.columns[-1]
        result_long = result.melt(id_vars=id_vars, value_vars=value_vars, var_name='indicator', value_name='value')

        # set creation_date to today's date
        result_long['creation_date'] = datetime.today().strftime('%Y-%m-%d')

        # set indicator_version to current max plus 1
        indicator_name = result_long['indicator'].unique()[0]
        geo_level = result_long['geo_level'].unique()[0]
        geo_parent_name = result_long['geo_parent_name'].unique()[0]
        latest_indicator_version = indicators[
            (indicators['indicator'] == indicator_name) &
            (indicators['geo_level'] == geo_level) &
            (indicators['geo_parent_name'] == geo_parent_name)
        ]['indicator_version'].max()

        if np.isnan(latest_indicator_version):
            latest_indicator_version = 0

        result_long['indicator_version'] = latest_indicator_version + 1

        # compare results locally
        if data_to_csv==True:
            export_df = pd.concat([indicators[
                (indicators['indicator'] == indicator_name) &
                (indicators['geo_level'] == geo_level) &
                (indicators['geo_parent_name'] == geo_parent_name)
            ], result_long], axis=0)

            export_df_wide = pd.pivot(export_df, index = ['geo_id', 'geo_level', 'geo_name', 'geo_parent_name', 'indicator'], 
                                      columns = 'indicator_version', values = 'value').reset_index()
            # export to csv
            export_df_wide.to_csv(f'{geo_parent_name}_{geo_level}_{indicator_name}.csv')
        
        # upload valid results to carto
        if data_to_carto==True:
            # upload indicators to carto
            to_carto(result_long, "indicators", if_exists='append')


def to_raster(gdf: GeoDataFrame, snap_to):
    """
    Rasterize the admin boundaries to the specified resolution.
    :param resolution: resolution in geographic coordinates of the output raster
    :return:
    """

    return make_geocube(
        vector_data=gdf,
        measurements=["index"],
        like=snap_to,
        geom=gdf.total_bounds
    ).index


def bounding_box(gdf):
    return box(*gdf.total_bounds)


def initialize_ee():
    _CREDENTIAL_FILE = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    GEE_SERVICE_ACCOUNT = os.environ["GOOGLE_APPLICATION_USER"]
    auth = ee.ServiceAccountCredentials(GEE_SERVICE_ACCOUNT, _CREDENTIAL_FILE)
    ee.Initialize(auth)


def get_geo_name(gdf: gpd.GeoDataFrame):
    if "geo_parent_name" in gdf.columns and "geo_level" in gdf.columns:
        geo_name = gdf["geo_parent_name"][0] + "-" + gdf["geo_level"][0]
        return geo_name
    else:
        loc_string = "__".join([str("{:.1f}".format(b)) for b in gdf.total_bounds]).replace(".", "_")
        return loc_string


def split_into_grids(region, gridSize):
    # Function to cut the region into grids when handling large GEE dataset
    bounds = ee.Geometry(region).bounds()
    coords = ee.List(bounds.coordinates().get(0))
    ll = ee.List(coords.get(0))
    ur = ee.List(coords.get(2))
    xmin = ll.get(0)
    xmax = ur.get(0)
    ymin = ll.get(1)
    ymax = ur.get(1)
    xrange = ee.Number(xmax).subtract(xmin)
    yrange = ee.Number(ymax).subtract(ymin)
    xSteps = xrange.divide(gridSize).ceil()
    ySteps = yrange.divide(gridSize).ceil()
    xList = ee.List.sequence(0, xSteps, gridSize)
    yList = ee.List.sequence(0, ySteps, gridSize)

    def map_x(x):
        def map_y(y):
            x1 = ee.Number(x).add(xmin)
            x2 = ee.Number(x).add(gridSize).add(xmin)
            y1 = ee.Number(y).add(ymin)
            y2 = ee.Number(y).add(gridSize).add(ymin)
            return ee.Geometry.Rectangle([x1, y1, x2, y2])
        return yList.map(map_y)

    return xList.map(map_x).flatten()
