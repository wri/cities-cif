from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_image_collection
from .layer_geometry import GeoExtent, retrieve_cached_city_data

DEFAULT_SPATIAL_RESOLUTION = 100

class BuiltUpHeight(Layer):
    OUTPUT_FILE_FORMAT = 'tif'
    MAJOR_LAYER_NAMING_ATTS = None
    MINOR_LAYER_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_s3_cache_retrieval=False):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        # Attempt to retrieve cached file based on layer_id.
        retrieved_cached_data = retrieve_cached_city_data(self, bbox, allow_s3_cache_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        # Notes for Heat project:
        # https://ghsl.jrc.ec.europa.eu/ghs_buH2023.php
        # ANBH is the average height of the built surfaces, USE THIS
        # AGBH is the amount of built cubic meters per surface unit in the cell
        # ee.ImageCollection("projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_R2023A")

        built_height = ee.Image("JRC/GHSL/P2023A/GHS_BUILT_H/2018")

        built_height_ic = ee.ImageCollection(built_height)
        ee_rectangle = bbox.to_ee_rectangle()
        data = get_image_collection(
            built_height_ic,
            ee_rectangle,
            spatial_resolution,
            "built up height"
        ).built_height

        return data
