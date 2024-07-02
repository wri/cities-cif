from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_utm_zone_epsg, get_image_collection


class UrbanLandUse(Layer):
    def __init__(self, band='b1', **kwargs):
        super().__init__(**kwargs)
        self.band = band

    def get_data(self, bbox):
        dataset = ee.ImageCollection("projects/wri-datalab/cities/SSC/LULC_V2")
        # ImageCollection didn't cover the globe
        if dataset.filterBounds(ee.Geometry.BBox(*bbox)).size().getInfo() == 0:
            ulu = ee.ImageCollection(ee.Image.constant(0)
                                     .clip(ee.Geometry.BBox(*bbox))
                                     .rename('lulc')
                                     )
        else:
            ulu = ee.ImageCollection(dataset
                                     .filterBounds(ee.Geometry.BBox(*bbox))
                                     .select(self.band)
                                     .reduce(ee.Reducer.firstNonNull())
                                     .rename('lulc')
                                     )

        data = get_image_collection(ulu, bbox, 1, "urban land use v2").lulc

        return data
