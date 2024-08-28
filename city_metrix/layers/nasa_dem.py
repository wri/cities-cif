import ee
import xee
import xarray as xr

from .layer import Layer, get_image_collection


class NasaDEM(Layer):
    def __init__(self, scale_meters=30, **kwargs):
        super().__init__(**kwargs)
        self.scale_meters = scale_meters

    def get_data(self, bbox):
        dataset = ee.Image("NASA/NASADEM_HGT/001")
        nasa_dem = ee.ImageCollection(ee.ImageCollection(dataset)
                                      .filterBounds(ee.Geometry.BBox(*bbox))
                                      .select('elevation')
                                      .mean()
                                      )
        data = get_image_collection(nasa_dem, bbox, self.scale_meters, "NASA DEM").elevation
        
        return data
