from .layer import Layer, get_utm_zone_epsg, get_image_collection

from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

class TreeCover(Layer):
    """
    Merged tropical and nontropical tree cover from WRI
    Attributes:
        min_tree_cover: minimum tree-cover values used for filtering results
        max_tree_cover: maximum tree-cover values used for filtering results
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    NO_DATA_VALUE = 255

    def __init__(self, min_tree_cover=None, max_tree_cover=None, spatial_resolution=10, **kwargs):
        super().__init__(**kwargs)
        self.min_tree_cover = min_tree_cover
        self.max_tree_cover = max_tree_cover
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        tropics = ee.ImageCollection('projects/wri-datalab/TropicalTreeCover')
        nontropics = ee.ImageCollection('projects/wri-datalab/TTC-nontropics')
        merged_ttc = tropics.merge(nontropics)
        ttc_image = merged_ttc.reduce(ee.Reducer.mean()).rename('ttc')

        data = get_image_collection(ee.ImageCollection(ttc_image), bbox, self.spatial_resolution, "tree cover").ttc

        if self.min_tree_cover is not None:
            data = data.where(data >= self.min_tree_cover)
        if self.max_tree_cover is not None:
            data = data.where(data <= self.max_tree_cover)

        return data

