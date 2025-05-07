import ee

from city_metrix.metrix_model import Layer, get_image_collection, GeoExtent
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 30

class Fabdem(Layer):
    GEOSPATIAL_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        fabdem = ee.ImageCollection("projects/sat-io/open-datasets/FABDEM")
        fabdem_mosaic = ee.ImageCollection(fabdem.mosaic())

        ee_rectangle = bbox.to_ee_rectangle()
        data = get_image_collection(
            fabdem_mosaic,
            ee_rectangle,
            spatial_resolution,
            "fabdem"
        ).b1

        return data
