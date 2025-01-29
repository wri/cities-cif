from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import GeoExtent, Layer, get_image_collection


DEFAULT_SPATIAL_RESOLUTION = 100

class ImperviousSurface(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        # load impervious_surface
        # change_year_index is zero if permeable as of 2018
        impervious_surface = ee.ImageCollection(ee.Image("Tsinghua/FROM-GLC/GAIA/v10").gt(0))

        ee_rectangle  = bbox.to_ee_rectangle()
        imperv_surf_ic = ee.ImageCollection(impervious_surface
                                            .filterBounds(ee_rectangle['ee_geometry'])
                                            .select('change_year_index')
                                            .sum()
                                            )

        data = get_image_collection(
            imperv_surf_ic,
            ee_rectangle,
            spatial_resolution,
            "imperv surf"
        ).change_year_index

        return data
