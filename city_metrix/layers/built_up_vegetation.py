from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from . import EsaWorldCoverClass, NdviSentinel2
from .layer import Layer, get_utm_zone_epsg, get_image_collection


class BuiltUpVegetation(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, land_cover_class=None, year=2021, spatial_resolution=10, **kwargs):
        super().__init__(**kwargs)
        self.land_cover_class = land_cover_class
        self.year = year
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        esa_data = None
        if self.year == 2020:
            esa_data = get_image_collection(
                ee.ImageCollection("ESA/WorldCover/v100"),
                bbox,
                self.spatial_resolution,
                "ESA world cover"
            ).Map
        elif self.year >= 2021:
            esa_data = get_image_collection(
                ee.ImageCollection("ESA/WorldCover/v200"),
                bbox,
                self.spatial_resolution,
                "ESA world cover"
            ).Map

        esa_data = esa_data.where(esa_data == EsaWorldCoverClass.BUILT_UP.value)

        ndvi_threshold = 0.4
        ndvi_data = (NdviSentinel2(year=self.year, spatial_resolution=self.spatial_resolution, ndvi_threshold=ndvi_threshold)
                     .get_data(bbox))

        return esa_data

