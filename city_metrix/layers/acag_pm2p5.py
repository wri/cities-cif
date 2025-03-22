from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_image_collection
from .layer_geometry import GeoExtent, retrieve_cached_city_data

DEFAULT_SPATIAL_RESOLUTION = 1113.1949


class AcagPM2p5(Layer):
    LAYER_ID = "acag_pm2p5"
    OUTPUT_FILE_FORMAT = 'tif'

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
                 resampling_method=None, allow_s3_cache_retrieval=False):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        retrieved_cached_data = retrieve_cached_city_data(bbox, self.LAYER_ID, self.year, self.OUTPUT_FILE_FORMAT
                                                          , allow_s3_cache_retrieval)
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
