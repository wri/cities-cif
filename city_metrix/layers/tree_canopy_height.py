from .layer import Layer, get_utm_zone_epsg, get_image_collection

from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

class TreeCanopyHeight(Layer):
    name = "tree_canopy_height"
    NO_DATA_VALUE = 0

    def __init__(self, scale_meters=1, **kwargs):
        super().__init__(**kwargs)
        self.scale_meters = scale_meters

    def get_data(self, bbox):
        canopy_ht = ee.ImageCollection("projects/meta-forest-monitoring-okw37/assets/CanopyHeight")
        # aggregate time series into a single image
        canopy_ht = canopy_ht.reduce(ee.Reducer.mean()).rename("cover_code")

        data = get_image_collection(ee.ImageCollection(canopy_ht), bbox,
                                    self.scale_meters, "tree canopy height")

        return data.cover_code
