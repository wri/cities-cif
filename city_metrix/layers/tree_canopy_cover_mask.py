import xarray as xr

from city_metrix.metrix_model import Layer, GeoExtent
from ..constants import GTIFF_FILE_EXTENSION
from .tree_canopy_height import TreeCanopyHeight
from city_metrix.metrix_dao import retrieve_cached_city_data

DEFAULT_SPATIAL_RESOLUTION = 1


class TreeCanopyCoverMask(Layer):
    GEOSPATIAL_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["height"]
    MINOR_NAMING_ATTS = ["percentage"]

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
                 resampling_method=None, allow_cache_retrieval=False):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        # Attempt to retrieve cached file based on layer_id.
        retrieved_cached_data = retrieve_cached_city_data(self, bbox, allow_cache_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        canopy_ht = TreeCanopyHeight(height=self.height).get_data(bbox, spatial_resolution)
        canopy_ht = canopy_ht.notnull().astype(int)

        canopy_ht_repojected = canopy_ht.coarsen(x=256, y=256, boundary="trim").mean() # 256 * 256 = 65536
        data = xr.where(canopy_ht_repojected >= self.percentage/100, 1, 0)

        utm_crs = bbox.as_utm_bbox().crs
        data = data.rio.write_crs(utm_crs)

        return data
