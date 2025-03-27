from .landsat_collection_2 import LandsatCollection2
from .layer import Layer, get_image_collection
from dask.diagnostics import ProgressBar
import ee
import xarray

from .layer_geometry import GeoExtent, retrieve_cached_city_data, build_s3_names

DEFAULT_SPATIAL_RESOLUTION = 30

class LandSurfaceTemperature(Layer):
    OUTPUT_FILE_FORMAT = 'tif'

    """
    Attributes:
        start_date: starting date for data retrieval
        end_date: ending date for data retrieval
    """
    def __init__(self, start_date="2013-01-01", end_date="2023-01-01", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def get_layer_names(self):
        layer_name, layer_id, file_format = build_s3_names(self, None, None)
        return layer_name, layer_id, file_format

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_s3_cache_retrieval=False):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        layer_name, layer_id, file_format = self.get_layer_names()
        retrieved_cached_data = retrieve_cached_city_data(bbox, layer_name, layer_id, file_format, allow_s3_cache_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        def cloud_mask(image):
            qa = image.select('QA_PIXEL')

            mask = qa.bitwiseAnd(1 << 3).Or(qa.bitwiseAnd(1 << 4))
            return image.updateMask(mask.Not())

        def apply_scale_factors(image):
            thermal_band = image.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15)
            return thermal_band

        l8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")

        ee_rectangle = bbox.to_ee_rectangle()
        l8_st = (l8
                 .select('ST_B10', 'QA_PIXEL')
                 .filter(ee.Filter.date(self.start_date, self.end_date))
                 .filterBounds(ee_rectangle['ee_geometry'])
                 .map(cloud_mask)
                 .map(apply_scale_factors)
                 .reduce(ee.Reducer.mean())
                 )

        l8_st_ic = ee.ImageCollection(l8_st)
        data = get_image_collection(
            l8_st_ic,
            ee_rectangle,
            spatial_resolution,
            "LST"
        ).ST_B10_mean

        return data
