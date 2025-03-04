from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_image_collection
from .layer_geometry import GeoExtent
from .tree_canopy_height import TreeCanopyHeight

DEFAULT_SPATIAL_RESOLUTION = 1


class TreeCanopyCoverMask(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
        height: minimum tree height used for filtering results
    """

    def __init__(self, height=None, percentage=30, **kwargs):
        super().__init__(**kwargs)
        self.height = height
        self.percentage = percentage

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        canopy_ht = TreeCanopyHeight(height=self.height).get_data(bbox, spatial_resolution)
        canopy_ht = canopy_ht.notnull().astype(int)

        ee_rectangle = bbox.to_ee_rectangle()

        canopy_ht_repojected = canopy_ht.coarsen(x=256, y=256, boundary="trim").mean() # 256 * 256 = 65536
        data = xr.where(canopy_ht_repojected >= self.percentage/100, 1, 0)

        utm_crs = bbox.as_utm_bbox().crs
        data = data.rio.write_crs(utm_crs)

        return data
