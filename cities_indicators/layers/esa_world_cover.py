from pystac_client import Client
from enum import Enum

from cities_indicators.city import City
from cities_indicators.layers.raster_layer import RasterLayer


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


class EsaWorldCover(RasterLayer):
    STAC_CATALOG_URI = "https://services.terrascope.be/stac/"
    STAC_COLLECTION_ID = "urn:eop:VITO:ESA_WorldCover_10m_2020_AWS_V1"
    STAC_ASSET_ID = "ESA_WORLDCOVER_10M_MAP"

    def get_layer_uris(self, city):
        catalog = Client.open(self.STAC_CATALOG_URI)
        search = catalog.search(
            max_items=20,
            collections=self.STAC_COLLECTION_ID,
            intersects=city.extent
        )

        uris = [
            item.assets[self.STAC_ASSET_ID].href
            for item in search.items()
        ]

        return uris

    def read(self, city: City, land_cover_class=None):
        data = super().read(city)

        if land_cover_class:
            return data.where(data == land_cover_class)

        return data

