from .layer import Layer, get_utm_zone_epsg, get_image_collection

from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee


class TreeCanopyHeight(Layer):
    
    name = "tree_canopy_hight"

    NO_DATA_VALUE = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox):
        canopy_ht = ee.ImageCollection("projects/meta-forest-monitoring-okw37/assets/CanopyHeight")
        # aggregate time series into a single image
        canopy_ht = canopy_ht.reduce(ee.Reducer.mean()).rename("cover_code")




        data = get_image_collection(ee.ImageCollection(canopy_ht), bbox, 1, "tree canopy hight")

        return data.cover_code

