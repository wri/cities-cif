import rioxarray
import xarray as xr
from typing import List
from pystac_client import Client
import ee

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
