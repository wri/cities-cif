from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_utm_zone_epsg, get_image_collection


class WorldPopAgeSex(Layer):
    def __init__(self, agesex_classes, year=2020, **kwargs):
        super().__init__(**kwargs)
		self.agesex_classes = agesex_classes
        self.year = year

    def get_data(self, bbox):
        # load population
        dataset = ee.ImageCollection('WorldPop/GP/100m/pop_age_sex')
        world_pop = ee.ImageCollection(dataset
                     .filterBounds(ee.Geometry.BBox(*bbox))
                     .filter(ee.Filter.inList('year', [self.year]))
                     .select(self.agesex_classes[0])
                     )
		for agesex_class in self.agesex_classes[1:]:
			world_pop = world_pop.add(
				ee.ImageCollection(dataset
                     .filterBounds(ee.Geometry.BBox(*bbox))
                     .filter(ee.Filter.inList('year', [self.year]))
                     .select(agesex_class)
                     )
			)
		world_pop = world_pop.sum()

        data = get_image_collection(world_pop, bbox, 100, "world pop")
        return data.population
