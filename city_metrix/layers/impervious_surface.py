import ee
import numpy as np
import xarray as xr

from city_metrix.metrix_model import Layer, get_image_collection, GeoExtent
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 100

class ImperviousSurface(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, year=2018, **kwargs):
        super().__init__(**kwargs)
        if year is not None and (year > 2018 or year < 1985):
            raise Exception('Dataset covers only 1985 through 2018')
        self.year = year

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        # load impervious_surface
        # change_year_index is zero if permeable as of 2018
        impervious_surface = ee.ImageCollection(ee.Image("Tsinghua/FROM-GLC/GAIA/v10"))

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

        if self.year is None:
            result = data.fillna(1)
        else:
            year_code = (2019 - self.year)
            result = xr.where(data >= year_code, 1, np.nan).rio.write_crs(bbox.as_utm_bbox().crs)

        return result
