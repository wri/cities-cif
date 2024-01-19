from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_utm_zone_epsg, get_image_collection


class UrbanLandUse(Layer):
    def __init__(self, band='lulc', **kwargs):
        super().__init__(**kwargs)
        self.band = band

    def get_data(self, bbox):
        dataset = ee.ImageCollection("projects/wri-datalab/cities/urban_land_use/V1")
        ulu = ee.ImageCollection(dataset
               .filterBounds(ee.Geometry.BBox(*bbox))
               .select(self.band)
               .reduce(ee.Reducer.firstNonNull())
               .rename('lulc')
               )

        data = get_image_collection(ulu, bbox, 5, "urban land use").lulc
        return data
