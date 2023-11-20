from pystac_client import Client
from enum import Enum
import odc.stac

from ..io import read_tiles, bounding_box


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

    def __init__(self, bbox, land_cover_class=None):
        catalog = Client.open(self.STAC_CATALOG_URI)
        query = catalog.search(
            collections=self.STAC_COLLECTION_ID,
            bbox=bbox,
        )

        self.data = odc.stac.load(
            query.items(),
            resolution=10,
            crs=4326,
            bbox=bbox,
            chunks={'x': 1024, 'y': 1024, 'time': 1},
            fail_on_error=False,
        )

        if land_cover_class:
            self.data = self.data.where(self.data == land_cover_class.value)






