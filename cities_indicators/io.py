import rioxarray
import xarray as xr
from typing import List
from pystac_client import Client
import ee
import geopandas as gpd
from cartoframes.auth import set_default_credentials
from cartoframes import read_carto, to_carto
from datetime import datetime

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
    set_default_credentials(username="wri-cities",
                            base_url="https://{user}.carto.com/".format(user="wri-cities"),
                            api_key="xxxx")
    # pull indicators table from Carto
    indicators = read_carto('indicators')
    
    # loop through results tables in the list
    for result in results:
        # conver from wide format to long format
        id_vars=['geo_id', 'geo_level', 'geo_name', 'geo_parent_name','creation_date']
        value_vars = result.columns[-1]
        result_long = result.melt(id_vars=id_vars, value_vars=value_vars, var_name='indicator', value_name='value')
        # set creation_date to today's date
        result_long['creation_date'] = datetime.today().strftime('%Y-%m-%d')
        # set indicator_version to current max plus 1
        indicators_sub = indicators[(indicators['indicator']==result_long['indicator'].unique()[0]) & (indicators['geo_level']==result_long['geo_level'].unique()[0]) & (indicators['geo_parent_name']==result_long['geo_parent_name'].unique()[0])]
        result_long['indicator_version'] = indicators_sub['indicator_version'].max()+1

        # UPLOAD INDICATORS TO CARTO
        to_carto(result_long, "indicators", if_exists='append')
    