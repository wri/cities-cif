from dask.diagnostics import ProgressBar
from enum import Enum
import xarray as xr
import ee

from .layer import Layer, get_image_collection
from .layer_geometry import GeoExtent, retrieve_cached_city_data


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

DEFAULT_SPATIAL_RESOLUTION = 10

class EsaWorldCover(Layer):
    STAC_CATALOG_URI = "https://services.terrascope.be/stac/"
    STAC_COLLECTION_ID = "urn:eop:VITO:ESA_WorldCover_10m_2020_AWS_V1"
    STAC_ASSET_ID = "ESA_WORLDCOVER_10M_MAP"
    OUTPUT_FILE_FORMAT = 'tif'

    """
    Attributes:
        land_cover_class: Enum value from EsaWorldCoverClass
        year: year used for data retrieval
    """
    def __init__(self, land_cover_class=None, year=2020, **kwargs):
        super().__init__(**kwargs)
        self.land_cover_class = land_cover_class
        self.year = year

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_s3_cache_retrieval=False):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        retrieved_cached_data = retrieve_cached_city_data(self, self.land_cover_class, None, bbox, allow_s3_cache_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        if self.year == 2020:
            esa_data_ic = ee.ImageCollection("ESA/WorldCover/v100")
        elif self.year == 2021:
            esa_data_ic = ee.ImageCollection("ESA/WorldCover/v200")
        else:
            raise ValueError(f'Specified year ({self.year}) is not currently supported')

        ee_rectangle  = bbox.to_ee_rectangle()
        data = get_image_collection(
            esa_data_ic,
            ee_rectangle,
            spatial_resolution,
            "ESA world cover"
        ).Map

        if self.land_cover_class:
            data = data.where(data == self.land_cover_class.value)

        return data
