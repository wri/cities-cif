import ee
import xee
import xarray as xr

from .layer import Layer, get_image_collection


class AlosDSM(Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox):
        dataset = ee.ImageCollection("JAXA/ALOS/AW3D30/V3_2")
        alos_dsm = ee.ImageCollection(dataset
                                      .filterBounds(ee.Geometry.BBox(*bbox))
                                      .select('DSM')
                                      .mean()
                                      )
        data = get_image_collection(alos_dsm, bbox, 30, "ALOS DSM").DSM

        return data
