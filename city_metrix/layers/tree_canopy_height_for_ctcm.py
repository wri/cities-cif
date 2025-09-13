import ee

from city_metrix.metrix_model import Layer, get_image_collection, GeoExtent
from ..constants import GTIFF_FILE_EXTENSION
from ..metrix_dao import extract_bbox_aoi

DEFAULT_SPATIAL_RESOLUTION = 1

class TreeCanopyHeightCTCM(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    PROCESSING_TILE_SIDE_M = 5000
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["height"]
    NO_DATA_VALUE = 0

    """
    Attributes:
        height: minimum tree height used for filtering results
    """
    def __init__(self, height=None, **kwargs):
        super().__init__(**kwargs)
        self.height = height

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        buffered_utm_bbox = bbox.buffer_utm_bbox(10)
        ee_rectangle  = buffered_utm_bbox.to_ee_rectangle()

        canopy_ht = ee.ImageCollection("projects/meta-forest-monitoring-okw37/assets/CanopyHeight")

        # aggregate time series into a single image
        canopy_ht_img = (canopy_ht
                         .reduce(ee.Reducer.mean())
                         .rename("cover_code")
                         )

        canopy_ht_ic = ee.ImageCollection(canopy_ht_img)
        data = get_image_collection(
            canopy_ht_ic,
            ee_rectangle,
            spatial_resolution,
            "tree canopy height"
        ).cover_code
        result_data = data.astype("uint8")

        if self.height:
            result_data = result_data.where(result_data >= self.height)

        utm_crs = ee_rectangle['crs']
        result_data = result_data.rio.write_crs(utm_crs)
        result_data['crs'] = utm_crs

        # Trim back to original AOI
        result_data = extract_bbox_aoi(result_data, bbox)

        return result_data
