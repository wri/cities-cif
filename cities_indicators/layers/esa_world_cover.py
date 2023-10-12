from pystac_client import Client
from enum import Enum

from cities_indicators.io import read_tiles, bounding_box


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


class EsaWorldCover:
    STAC_CATALOG_URI = "https://services.terrascope.be/stac/"
    STAC_COLLECTION_ID = "urn:eop:VITO:ESA_WorldCover_10m_2020_AWS_V1"
    STAC_ASSET_ID = "ESA_WORLDCOVER_10M_MAP"

    def get_tile_uris(self, gdf):
        catalog = Client.open(self.STAC_CATALOG_URI)
        search = catalog.search(
            max_items=20,
            collections=self.STAC_COLLECTION_ID,
            intersects=bounding_box(gdf)
        )

        uris = [
            item.assets[self.STAC_ASSET_ID].href
            for item in search.items()
        ]

        return uris

    def read(self, gdf, snap_to=None, land_cover_class: EsaWorldCoverClass=None):
        data = read_tiles(gdf, self.get_tile_uris(gdf), snap_to)
        if land_cover_class:
            return data.where(data == land_cover_class.value)

        return data

