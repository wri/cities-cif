from dask.diagnostics import ProgressBar
from enum import Enum
import xarray as xr
import ee

from .layer import Layer, get_utm_zone_epsg, get_image_collection


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
    """
    Attributes:
        land_cover_class: Enum value from EsaWorldCoverClass
        year: year used for data retrieval
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    STAC_CATALOG_URI = "https://services.terrascope.be/stac/"
    STAC_COLLECTION_ID = "urn:eop:VITO:ESA_WorldCover_10m_2020_AWS_V1"
    STAC_ASSET_ID = "ESA_WORLDCOVER_10M_MAP"

    def __init__(self, land_cover_class=None, year=2020, spatial_resolution=10, **kwargs):
        super().__init__(**kwargs)
        self.land_cover_class = land_cover_class
        self.year = year
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        if self.year == 2020:
            esa_data_ic = ee.ImageCollection("ESA/WorldCover/v100")
        elif self.year == 2021:
            esa_data_ic = ee.ImageCollection("ESA/WorldCover/v200")
        else:
            raise ValueError(f'Specified year ({self.year}) is not currently supported')

        data = get_image_collection(
            esa_data_ic,
            bbox,
            self.spatial_resolution,
            "ESA world cover"
        ).Map

        if self.land_cover_class:
            data = data.where(data == self.land_cover_class.value)

        return data
