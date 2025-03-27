from .layer import Layer, get_image_collection

from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer_geometry import GeoExtent, retrieve_cached_city_data, build_s3_names

DEFAULT_SPATIAL_RESOLUTION = 10

class TreeCover(Layer):
    OUTPUT_FILE_FORMAT = 'tif'
    NO_DATA_VALUE = 255

    """
    Merged tropical and nontropical tree cover from WRI
    Attributes:
        min_tree_cover: minimum tree-cover values used for filtering results
        max_tree_cover: maximum tree-cover values used for filtering results
    """
    def __init__(self, min_tree_cover=None, max_tree_cover=None, **kwargs):
        super().__init__(**kwargs)
        self.min_tree_cover = min_tree_cover
        self.max_tree_cover = max_tree_cover

    def get_layer_names(self):
        min_tree_cover_str = "" if self.min_tree_cover is None else f"min{self.min_tree_cover}"
        max_tree_cover_str = "" if self.max_tree_cover is None else f"max{self.max_tree_cover}"
        qualifier = min_tree_cover_str+max_tree_cover_str
        layer_name, layer_id, file_format = build_s3_names(self, qualifier, None)
        return layer_name, layer_id, file_format

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_s3_cache_retrieval=False):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        layer_name, layer_id, file_format = self.get_layer_names()
        retrieved_cached_data = retrieve_cached_city_data(bbox, layer_name, layer_id, file_format, allow_s3_cache_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

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
