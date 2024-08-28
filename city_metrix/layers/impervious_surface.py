from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_utm_zone_epsg, get_image_collection


class ImperviousSurface(Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox):
        # load impervious_surface
        dataset = ee.ImageCollection(ee.Image("Tsinghua/FROM-GLC/GAIA/v10").gt(0))  # change_year_index is zero if permeable as of 2018
        imperv_surf = ee.ImageCollection(dataset
                     .filterBounds(ee.Geometry.BBox(*bbox))
                     .select('change_year_index')
                     .sum()
                     )

        data = get_image_collection(imperv_surf, bbox, 100, "imperv surf")
        return data.change_year_index
