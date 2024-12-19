from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_image_collection


class UrbanLandUse(Layer):
    """
    Attributes:
        band: raster band used for data retrieval
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, band='lulc', spatial_resolution=5, **kwargs):
        super().__init__(**kwargs)
        self.band = band
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        ulu = ee.ImageCollection("projects/wri-datalab/cities/urban_land_use/V1")

        # ImageCollection didn't cover the globe
        if ulu.filterBounds(ee.Geometry.BBox(*bbox)).size().getInfo() == 0:
            ulu_ic = ee.ImageCollection(ee.Image
                                     .constant(0)
                                     .clip(ee.Geometry.BBox(*bbox))
                                     .rename('lulc')
                                     )
        else:
            ulu_ic = ee.ImageCollection(ulu
                                     .filterBounds(ee.Geometry.BBox(*bbox))
                                     .select(self.band)
                                     .reduce(ee.Reducer.firstNonNull())
                                     .rename('lulc')
                                     )

        data = get_image_collection(
            ulu_ic,
            bbox,
            self.spatial_resolution,
            "urban land use"
        ).lulc

        return data
