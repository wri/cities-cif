from .landsat_collection_2 import LandsatCollection2
from .layer import Layer, get_utm_zone_epsg

from shapely.geometry import box
import datetime
import ee
import xarray


class LandSurfaceTemperature(Layer):
    def __init__(self, start_date="2013-01-01", end_date="2023-01-01", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def get_data(self, bbox):
        def cloud_mask(image):
            qa = image.select('QA_PIXEL')
            mask = qa.bitwiseAnd(1 << 3).Or(qa.bitwiseAnd(1 << 4))
            return image.updateMask(mask.Not())

        def apply_scale_factors(image):
            thermal_band = image.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15)
            return thermal_band

        l8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        l8_st = l8 \
            .select('ST_B10', 'QA_PIXEL') \
            .filter(ee.Filter.date(self.start_date, self.end_date)) \
            .filterBounds(ee.Geometry.BBox(*bbox)) \
            .map(cloud_mask) \
            .map(apply_scale_factors) \
            .reduce(ee.Reducer.mean())

        crs = get_utm_zone_epsg(bbox)

        ds = xarray.open_dataset(
            ee.ImageCollection(l8_st),
            engine='ee',
            scale=30,
            crs=crs,
            geometry=ee.Geometry.BBox(*bbox),
        )
        ds = ds.compute()

        data = ds.ST_B10_mean.squeeze("time").transpose("Y", "X").rename({'X': 'x', 'Y': 'y'})
        return data

    def write(self, output_path):
        self.data.rio.to_raster(output_path)


