from .layer import Layer, get_utm_zone_epsg

from rioxarray.raster_array import RasterArray
import xarray as xr
import xee
import ee


class UrbanLandUse(Layer):
    def __init__(self, band=None, **kwargs):
        super().__init__(**kwargs)
        self.band = band

    def get_data(self, bbox):
        crs = get_utm_zone_epsg(bbox)
        dataset = ee.ImageCollection("projects/wri-datalab/cities/urban_land_use/V1")
        ulu = (dataset
               .filterBounds(ee.Geometry.BBox(*bbox))
               .select(self.band)
               .reduce(ee.Reducer.firstNonNull())
               .rename('lulc')
               )
        
        ds = xr.open_dataset(
            ee.ImageCollection(ulu),
            engine='ee',
            scale=5,
            crs=crs,
            geometry=ee.Geometry.Rectangle(*bbox)
        )

        data = ds.lulc.compute()

        # get in rioxarray format
        data = data.squeeze("time").transpose("Y", "X").rename({'X': 'x', 'Y': 'y'})

        return data
