import ee

from .layer import Layer, get_image_collection
from city_metrix.metrix_dao import retrieve_cached_city_data
from .layer_geometry import GeoExtent
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 1

class TreeCanopyHeight(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_LAYER_NAMING_ATTS = ["height"]
    MINOR_LAYER_NAMING_ATTS = None
    NO_DATA_VALUE = 0

    """
    Attributes:
        height: minimum tree height used for filtering results
    """
    def __init__(self, height=None, **kwargs):
        super().__init__(**kwargs)
        self.height = height

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_cache_retrieval=False):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        # Attempt to retrieve cached file based on layer_id.
        retrieved_cached_data = retrieve_cached_city_data(self, bbox, allow_cache_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        canopy_ht = ee.ImageCollection("projects/meta-forest-monitoring-okw37/assets/CanopyHeight")

        # aggregate time series into a single image
        canopy_ht_img = (canopy_ht
                         .reduce(ee.Reducer.mean())
                         .rename("cover_code")
                         )

        canopy_ht_ic = ee.ImageCollection(canopy_ht_img)
        ee_rectangle = bbox.to_ee_rectangle()
        data = get_image_collection(
            canopy_ht_ic,
            ee_rectangle,
            spatial_resolution,
            "tree canopy height"
        ).cover_code

        if self.height:
            data = data.where(data >= self.height)
        
        utm_crs = bbox.as_utm_bbox().crs
        data = data.rio.write_crs(utm_crs)

        return data
