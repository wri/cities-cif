from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_utm_zone_epsg, get_image_collection

class WorldPop(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, spatial_resolution=100, **kwargs):
        super().__init__(**kwargs)
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        # load population
        dataset = ee.ImageCollection('WorldPop/GP/100m/pop')
        world_pop = ee.ImageCollection(dataset
                     .filterBounds(ee.Geometry.BBox(*bbox))
                     .filter(ee.Filter.inList('year', [2020]))
                     .select('population')
                     .mean()
                     )

        data = get_image_collection(world_pop, bbox, self.spatial_resolution, "world pop")
        return data.population
