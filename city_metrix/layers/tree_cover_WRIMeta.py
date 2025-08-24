import xarray as xr
import numpy as np
from city_metrix.metrix_model import Layer, GeoExtent
from ..constants import GTIFF_FILE_EXTENSION
from .tree_canopy_height import TreeCanopyHeight

DEFAULT_SPATIAL_RESOLUTION = 1


class TreeCanopyCoverMask(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["height", "percentage"]

    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
        height: minimum tree height used for filtering results
    """

    def __init__(self, height=None, percentage=30, spatial_resolution=None, **kwargs):
        super().__init__(**kwargs)
        self.height = height
        self.percentage = percentage
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        if spatial_resolution is not None:
            spatial_resolution = spatial_resolution
        elif self.spatial_resolution is not None:
            spatial_resolution = self.spatial_resolution
        else:
            spatial_resolution = DEFAULT_SPATIAL_RESOLUTION

        canopy_ht = TreeCanopyHeight(height=self.height).get_data(bbox, spatial_resolution)
        canopy_ht = canopy_ht.notnull().astype(int)

        canopy_ht_repojected = canopy_ht.coarsen(x=10, y=10, boundary="trim").mean() # 256 * 256 = 65536
        data = xr.where(canopy_ht_repojected >= self.percentage/100, 1, np.nan)

        utm_crs = bbox.as_utm_bbox().crs
        data = data.rio.write_crs(utm_crs)

        return data
