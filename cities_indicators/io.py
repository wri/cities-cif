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

from cities_indicators.city import City


def read_vrt(city: City, vrt_uri: str, resolution: int):
    return read_tiles(city, [vrt_uri], resolution)


def read_tiles(city: City, tile_uris: List[str], resolution: int):
    # read and clip to city extent
    windows = []
    for layer_uri in tile_uris:
        ds = rioxarray.open_rasterio(layer_uri)
        window = ds.rio.clip_box(*city.bounds)
        windows.append(window)

    if len(windows) > 1:
        unaligned_data = xr.concat(windows).squeeze("band")
    else:
        unaligned_data = windows[0].squeeze("band")

    # make sure the boundaries align with city analysis
    city_raster = city.to_raster(resolution)
    aligned_data = unaligned_data.rio.reproject_match(city_raster).assign_coords({
        "x": city_raster.x,
        "y": city_raster.y,
    })

    return aligned_data


def read_gee(city: City, asset_id: str):
    # read imagecollection
    ImgColl = ee.ImageCollection(asset_id)
    # reduce image collection to image
    Img = ImgColl.reduce(ee.Reducer.mean()).rename('b1')
    # clip to city extent
    data = Img.clip(ee.Geometry.BBox(*city.bounds))
    
    return data


def export_carto(results: List[gpd.GeoDataFrame]):
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

        # UPLOAD INDICATORS TO CARTO
        to_carto(result_long, "indicators", if_exists='append')

results=indicators
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
        result = results[0]
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
            export_df_wide.to_csv(f'{geo_parent_name}_{geo_level}_{indicator_name}.csv')
        
        # upload valid results to carto
        if data_to_carto==True:
            # upload indicators to carto
            to_carto(result_long, "indicators", if_exists='append')
