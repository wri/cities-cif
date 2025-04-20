import ee

from city_metrix.metrix_model import Layer, get_image_collection, GeoExtent
from ..constants import GTIFF_FILE_EXTENSION, GeoType
from ..metrix_dao import write_layer
from ..repo_manager import retrieve_cached_city_data2

DEFAULT_SPATIAL_RESOLUTION = 100

class BuiltUpHeight(Layer):
    GEOSPATIAL_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, force_data_refresh=False):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        # Attempt to retrieve cached file based on layer_id.
        retrieved_cached_data, file_uri = retrieve_cached_city_data2(self, bbox, force_data_refresh)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        # Notes for Heat project:
        # https://ghsl.jrc.ec.europa.eu/ghs_buH2023.php
        # ANBH is the average height of the built surfaces, USE THIS
        # AGBH is the amount of built cubic meters per surface unit in the cell
        # ee.ImageCollection("projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_R2023A")

        built_height = ee.Image("JRC/GHSL/P2023A/GHS_BUILT_H/2018")

        built_height_ic = ee.ImageCollection(built_height)
        ee_rectangle = bbox.to_ee_rectangle()
        data = get_image_collection(
            built_height_ic,
            ee_rectangle,
            spatial_resolution,
            "built up height"
        ).built_height

        if bbox.geo_type == GeoType.CITY:
            write_layer(data, file_uri, self.GEOSPATIAL_FILE_FORMAT)

        return data
