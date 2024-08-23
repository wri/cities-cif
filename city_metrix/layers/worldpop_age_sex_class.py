from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_utm_zone_epsg, get_image_collection


class WorldPop(Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
		self.agesex_classes = agesex_classes

    def get_data(self, bbox):
        # load population
        dataset = ee.ImageCollection('WorldPop/GP/100m/pop_age_sex')
        world_pop = ee.ImageCollection(dataset
                     .filterBounds(ee.Geometry.BBox(*bbox))
                     .filter(ee.Filter.inList('year', [2020]))
                     .select(self.agesex_classes[0])
                     )
		for agesex_class in self.agesex_classes[1:]:
			world_pop = world_pop.add(
				ee.ImageCollection(dataset
                     .filterBounds(ee.Geometry.BBox(*bbox))
                     .filter(ee.Filter.inList('year', [2020]))
                     .select(agesex_class)
                     )
			)
		world_pop = world_pop.mean()  # Should this be sum?

        data = get_image_collection(world_pop, bbox, 100, "world pop")
        return data.population
