from .layer import GeoExtent, Layer, get_image_collection

from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee


DEFAULT_SPATIAL_RESOLUTION = 10

class TreeCover(Layer):
    """
    Merged tropical and nontropical tree cover from WRI
    Attributes:
        min_tree_cover: minimum tree-cover values used for filtering results
        max_tree_cover: maximum tree-cover values used for filtering results
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    NO_DATA_VALUE = 255

    def __init__(self, min_tree_cover=None, max_tree_cover=None, **kwargs):
        super().__init__(**kwargs)
        self.min_tree_cover = min_tree_cover
        self.max_tree_cover = max_tree_cover


    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        tropics = ee.ImageCollection('projects/wri-datalab/TropicalTreeCover')
        non_tropics = ee.ImageCollection('projects/wri-datalab/TTC-nontropics')

        merged_ttc = tropics.merge(non_tropics)
        ttc_image = (merged_ttc
                     .reduce(ee.Reducer.mean())
                     .rename('ttc')
                     )

        ttc_ic = ee.ImageCollection(ttc_image)
        ee_rectangle = bbox.to_ee_rectangle()
        data = get_image_collection(
            ttc_ic,
            ee_rectangle,
            spatial_resolution,
            "tree cover"
        ).ttc

        if self.min_tree_cover is not None:
            data = data.where(data >= self.min_tree_cover)
        if self.max_tree_cover is not None:
            data = data.where(data <= self.max_tree_cover)

        return data
