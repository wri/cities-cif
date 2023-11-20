import rioxarray

from .layer import Layer
from ..city import City
from ..io import read_tiles, read_gee

import xarray as xr
import geopandas as gpd
from shapely.geometry import box


class TropicalTreeCover(Layer):
    EXTENTS_URI = "gs://gee-exports/tropical-tree-cover/2020/tropical-tree-cover-2020-extents.geojson"
    NO_DATA_VALUE = -99
    TML = "projects/wri-datalab/TropicalTreeCover"

    def __init__(self, min_tree_cover=None, **kwargs):
        super().__init__(**kwargs)
        self.min_tree_cover = min_tree_cover

    def get_data(self, bbox):
        extents = gpd.read_file(self.EXTENTS_URI)
        bbox_poly = box(*bbox)

        intersecting_extents = extents[extents.intersects(bbox_poly)]
        centroid_extent = intersecting_extents[intersecting_extents.intersects(bbox_poly.centroid)].geometry.iloc[0]
        final_extents = intersecting_extents[~intersecting_extents.overlaps(centroid_extent)]

        tiles = []
        for layer_uri in final_extents['uri']:
            ds = rioxarray.open_rasterio(layer_uri)
            tile = ds.rio.clip_box(*bbox)
            tiles.append(tile)

        data = xr.combine_by_coords(tiles).squeeze("band")

        if self.min_tree_cover:
            data = data.where(data >= self.min_tree_cover)

        return data

