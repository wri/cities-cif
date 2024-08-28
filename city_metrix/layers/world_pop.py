from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_utm_zone_epsg, get_image_collection

class WorldPop(Layer):
    def __init__(self, scale_meters=100, **kwargs):
        super().__init__(**kwargs)
        self.scale_meters = scale_meters

    def get_data(self, bbox):
        # load population
        dataset = ee.ImageCollection('WorldPop/GP/100m/pop')
        world_pop = ee.ImageCollection(dataset
                     .filterBounds(ee.Geometry.BBox(*bbox))
                     .filter(ee.Filter.inList('year', [2020]))
                     .select('population')
                     .mean()
                     )

        data = get_image_collection(world_pop, bbox, self.scale_meters, "world pop")
        return data.population
