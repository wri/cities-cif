from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from . import EsaWorldCoverClass
from .layer import Layer, get_utm_zone_epsg, get_image_collection


class BuiltUpVegetation(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, land_cover_class=None, year=2020, spatial_resolution=10, **kwargs):
        super().__init__(**kwargs)
        self.land_cover_class = land_cover_class
        self.year = year
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        data = None
        if self.year == 2020:
            data = get_image_collection(
                ee.ImageCollection("ESA/WorldCover/v100"),
                bbox,
                self.spatial_resolution,
                "ESA world cover"
            ).Map
        elif self.year >= 2021:
            data = get_image_collection(
                ee.ImageCollection("ESA/WorldCover/v200"),
                bbox,
                self.spatial_resolution,
                "ESA world cover"
            ).Map

        # built_up_class = EsaWorldCoverClass.BUILT_UP
        data.where(data == self.land_cover_class.value)
        
        # built_height = ee.Image("JRC/GHSL/P2023A/GHS_BUILT_H/2018")
        # data = get_image_collection(ee.ImageCollection(built_height), bbox, self.spatial_resolution, "built up height")
        #

        p = 2

        return data

