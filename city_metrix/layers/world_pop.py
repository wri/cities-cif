from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_utm_zone_epsg, get_image_collection

class WorldPop(Layer):
    """
    Attributes:
        year: year used for data retrieval
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, year=2020, spatial_resolution=100, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        # load population
        dataset = ee.ImageCollection('WorldPop/GP/100m/pop')
        world_pop = ee.ImageCollection(dataset
                     .filterBounds(ee.Geometry.BBox(*bbox))
                     .filter(ee.Filter.inList('year', [self.year]))
                     .select('population')
                     .mean()
                     )

        data = get_image_collection(world_pop, bbox, self.spatial_resolution, "world pop")
        return data.population
