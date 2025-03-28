from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee
import numpy as np

from .layer import Layer, get_image_collection
from .layer_geometry import GeoExtent, retrieve_cached_city_data, build_s3_names

DEFAULT_SPATIAL_RESOLUTION = 5

class UrbanLandUse(Layer):
    OUTPUT_FILE_FORMAT = 'tif'

    """
    Attributes:
        band: raster band used for data retrieval
        ulu_class: urban land use class value used to filter the land use type
                   0 (open space), 1 (non-res), 2 (Atomistic), 3 (Informal), 4 (Formal), 5 (Housing project)
    """
    def __init__(self, band='lulc', ulu_class=None, **kwargs):
        super().__init__(**kwargs)
        self.band = band
        self.ulu_class = ulu_class

    def get_layer_names(self):
        qualifier = "" if self.band is None else f"__{self.band}"
        minor_qualifier = "" if self.ulu_class is None else f"__ulu{self.ulu_class}"
        layer_name, layer_id, file_format = build_s3_names(self, qualifier, minor_qualifier)
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

        ulu = ee.ImageCollection("projects/wri-datalab/cities/urban_land_use/V1")

        # ImageCollection didn't cover the global
        ee_rectangle = bbox.to_ee_rectangle()
        if ulu.filterBounds(ee_rectangle['ee_geometry']).size().getInfo() == 0:
            ulu_ic = ee.ImageCollection(ee.Image
                                     .constant(0)
                                     .clip(ee_rectangle['ee_geometry'])
                                     .rename('lulc')
                                     )
        else:
            ulu_ic = ee.ImageCollection(ulu
                                     .filterBounds(ee_rectangle['ee_geometry'])
                                     .select(self.band)
                                     .reduce(ee.Reducer.firstNonNull())
                                     .rename('lulc')
                                     )

        data = get_image_collection(
            ulu_ic,
            ee_rectangle,
            spatial_resolution,
            "urban land use"
        ).lulc

        if self.ulu_class:
            data = data.where(data == self.ulu_class, np.nan)

        return data
