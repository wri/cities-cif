from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_utm_zone_epsg, get_image_collection


class BuiltUpHeight(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, spatial_resolution=100, **kwargs):
        super().__init__(**kwargs)
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        # Notes for Heat project:
        # https://ghsl.jrc.ec.europa.eu/ghs_buH2023.php
        # ANBH is the average height of the built surfaces, USE THIS
        # AGBH is the amount of built cubic meters per surface unit in the cell
        # ee.ImageCollection("projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_R2023A")
        
        built_height = ee.Image("JRC/GHSL/P2023A/GHS_BUILT_H/2018")
        data = get_image_collection(ee.ImageCollection(built_height), bbox, self.spatial_resolution, "built up height")
        return data.built_height

