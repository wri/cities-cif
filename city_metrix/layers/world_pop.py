from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_utm_zone_epsg


class WorldPop(Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox):
        crs = get_utm_zone_epsg(bbox)
        # load population
        dataset = ee.ImageCollection('WorldPop/GP/100m/pop')
        world_pop = (dataset
                     .filterBounds(ee.Geometry.BBox(*bbox))
                     .filter(ee.Filter.inList('year', [2020]))
                     .select('population')
                     .mean()
                     )

        ds = xr.open_dataset(
            ee.ImageCollection(world_pop),
            engine='ee',
            scale=100,
            crs=crs,
            geometry=ee.Geometry.Rectangle(*bbox),
            chunks={'X': 512, 'Y': 512}
        )

        with ProgressBar():
            print("Extracting World Pop layer:")
            data = ds.population.compute()

        # get in rioxarray format
        data = data.squeeze("time").transpose("Y", "X").rename({'X': 'x', 'Y': 'y'})

        return data
