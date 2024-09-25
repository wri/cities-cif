from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_utm_zone_epsg, get_image_collection
from city_metrix.layers import WorldPop


class WorldPopAgeSex(Layer):
    """
    Attributes:
        agesex_classes: list of age-sex classes to retrieve
        year: year used for data retrieval
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, agesex_classes=[], year=2020, spatial_resolution=100, **kwargs):
        super().__init__(**kwargs)
        self.agesex_classes = agesex_classes
        self.year = year
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        # If no agesex classes requested, return plain WorldPop
        if not self.agesex_classes:
            return WorldPop().get_data(bbox)
        
        dataset = ee.ImageCollection('WorldPop/GP/100m/pop_age_sex')
        
		# Sum over agesex classes
        world_pop = ee.Image(0)
        for agesex_class in self.agesex_classes:
            tmp = dataset.filterBounds(ee.Geometry.BBox(*bbox))\
                           .filter(ee.Filter.inList('year', [self.year]))\
                           .select(agesex_class)\
                           .mean()
            world_pop = world_pop.add(tmp)

        world_pop = ee.ImageCollection(world_pop.reduce(ee.Reducer.sum()).rename('sum_age_sex_group'))

        data = get_image_collection(world_pop, bbox, self.spatial_resolution, "world pop age sex")
        return data.sum_age_sex_group
