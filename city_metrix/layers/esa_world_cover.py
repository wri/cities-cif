from pystac_client import Client
from enum import Enum
import rioxarray
import xarray as xr

from .layer import Layer


class EsaWorldCoverClass(Enum):
    TREE_COVER = 10
    SHRUBLAND = 20
    GRASSLAND = 30
    CROPLAND = 40
    BUILT_UP = 50
    BARE_OR_SPARSE_VEGETATION = 60
    SNOW_AND_ICE = 70
    PERMANENT_WATER_BODIES = 80
    HERBACEOUS_WET_LAND = 90
    MANGROVES = 95
    MOSS_AND_LICHEN = 100


class EsaWorldCover(Layer):
    STAC_CATALOG_URI = "https://services.terrascope.be/stac/"
    STAC_COLLECTION_ID = "urn:eop:VITO:ESA_WorldCover_10m_2020_AWS_V1"
    STAC_ASSET_ID = "ESA_WORLDCOVER_10M_MAP"

    def __init__(self, land_cover_class=None, **kwargs):
        super().__init__(**kwargs)
        self.land_cover_class = land_cover_class

    def get_data(self, bbox):
        catalog = Client.open(self.STAC_CATALOG_URI)
        query = catalog.search(
            collections=self.STAC_COLLECTION_ID,
            bbox=bbox,
        )

        # read URIs directly to get native resolution
        uris = [
            item.assets[self.STAC_ASSET_ID].href
            for item in query.items()
        ]

        tiles = []
        for layer_uri in uris:
            ds = rioxarray.open_rasterio(layer_uri)
            tile = ds.rio.clip_box(*bbox)
            tiles.append(tile)

        data = xr.combine_by_coords(tiles).squeeze("band")

        if self.land_cover_class:
            data = data.where(data == self.land_cover_class.value)

        return data






