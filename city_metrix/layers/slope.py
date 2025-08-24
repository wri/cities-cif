import ee
import xarray as xr
import numpy as np
from city_metrix.metrix_model import Layer, get_image_collection, GeoExtent
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 30

class Slope(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    """
   Slope from NASADEM, a reanalysis of year-2000 SRTM data
   Unit is degrees

    """
    def __init__(self, min_threshold=None, **kwargs):
        super().__init__(**kwargs)
        self.min_threshold = min_threshold

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, force_data_refresh=False):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        dem_img = ee.Image("NASA/NASADEM_HGT/001").select('elevation')
        slope_img = ee.Terrain.slope(dem_img)
        ee_rectangle  = bbox.to_ee_rectangle()

        data = get_image_collection(
                ee.ImageCollection(slope_img),
                ee_rectangle,
                spatial_resolution,
                "slope",
            ).slope

        if self.min_threshold is not None:
            data = xr.where(data >= self.min_threshold, 1, np.nan).assign_attrs(data.attrs).rio.write_crs(data.crs)

        return data
