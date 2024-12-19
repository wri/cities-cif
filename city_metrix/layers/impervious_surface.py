from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_utm_zone_epsg, get_image_collection


class ImperviousSurface(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, spatial_resolution=100, **kwargs):
        super().__init__(**kwargs)
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        # load impervious_surface
        # change_year_index is zero if permeable as of 2018
        impervious_surface = ee.ImageCollection(ee.Image("Tsinghua/FROM-GLC/GAIA/v10").gt(0))

        imperv_surf_ic = ee.ImageCollection(impervious_surface
                                            .filterBounds(ee.Geometry.BBox(*bbox))
                                            .select('change_year_index')
                                            .sum()
                                            )

        data = get_image_collection(
            imperv_surf_ic,
            bbox,
            self.spatial_resolution,
            "imperv surf"
        ).change_year_index

        return data
