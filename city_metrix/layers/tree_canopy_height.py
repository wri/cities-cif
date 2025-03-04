from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee
import numpy as np

from .layer import Layer, get_image_collection
from .layer_geometry import GeoExtent

DEFAULT_SPATIAL_RESOLUTION = 1

class TreeCanopyHeight(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
        height: minimum tree height used for filtering results
    """

    name = "tree_canopy_height"
    NO_DATA_VALUE = 0

    def __init__(self, height=None, **kwargs):
        super().__init__(**kwargs)
        self.height = height

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        canopy_ht = ee.ImageCollection("projects/meta-forest-monitoring-okw37/assets/CanopyHeight")

        # aggregate time series into a single image
        canopy_ht_img = (canopy_ht
                         .reduce(ee.Reducer.mean())
                         .rename("cover_code")
                         )

        canopy_ht_ic = ee.ImageCollection(canopy_ht_img)
        ee_rectangle = bbox.to_ee_rectangle()
        data = get_image_collection(
            canopy_ht_ic,
            ee_rectangle,
            spatial_resolution,
            "tree canopy height"
        ).cover_code

        if self.height:
            data = data.where(data >= self.height, np.nan)

        return data
