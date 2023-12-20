from dask.diagnostics import ProgressBar
from enum import Enum
import xarray as xr
import ee

from .layer import Layer, get_utm_zone_epsg


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
        esa = ee.ImageCollection("ESA/WorldCover/v100")
        crs = get_utm_zone_epsg(bbox)

        ds = xr.open_dataset(
            esa,
            engine='ee',
            scale=10,
            crs=crs,
            geometry=ee.Geometry.Rectangle(*bbox),
            chunks={'X': 512, 'Y': 512},
        )

        with ProgressBar():
            print("Extracting ESA world cover layer:")
            data = ds.Map.compute()

        data = data.squeeze("time").transpose("Y", "X").rename({'X': 'x', 'Y': 'y'})

        if self.land_cover_class:
            data = data.where(data == self.land_cover_class.value)

        return data






