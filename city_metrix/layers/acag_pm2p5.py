from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_image_collection
from .layer_dao import retrieve_cached_city_data
from .layer_geometry import GeoExtent
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 1113.1949


class AcagPM2p5(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_LAYER_NAMING_ATTS = None
    MINOR_LAYER_NAMING_ATTS = ["return_above"]
    """
    Attributes:
        year: only available year is 2022
        return_above:
    """
    def __init__(self, year=2022, return_above=0, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.return_above = return_above

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_cache_retrieval=False):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        # Attempt to retrieve cached file based on layer_id.
        retrieved_cached_data = retrieve_cached_city_data(self, bbox, allow_cache_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        acag_data = ee.Image(f'projects/wri-datalab/cities/aq/acag_annual_pm2p5_{self.year}')

        ee_rectangle  = bbox.to_ee_rectangle()
        data = get_image_collection(
            ee.ImageCollection(acag_data),
            ee_rectangle,
            spatial_resolution,
            "mean pm2.5 concentration"
        ).b1

        data = data.where(data >= self.return_above)

        return data
