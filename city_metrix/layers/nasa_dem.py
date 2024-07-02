import ee
import xee
import xarray as xr
from city_metrix.layers.layer import Layer, get_image_collection

class NasaDEM(Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox):
        dataset = ee.Image("NASA/NASADEM_HGT/001")
        nasa_dem = ee.ImageCollection(ee.ImageCollection(dataset)
                                      .filterBounds(ee.Geometry.BBox(*bbox))
                                      .select('elevation')
                                      .mean()
                                      )
        data = get_image_collection(nasa_dem, bbox, 30, "NASA DEM").elevation
        
        return data
