import ee

from city_metrix.metrix_model import (Layer, get_image_collection, set_resampling_for_continuous_raster,
                                      validate_raster_resampling_method, GeoExtent)
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 30
DEFAULT_RESAMPLING_METHOD = 'bilinear'

class AlosDSM(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method:str=DEFAULT_RESAMPLING_METHOD):

        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)

        alos_dsm = ee.ImageCollection("JAXA/ALOS/AW3D30/V3_2")

        ee_rectangle  = bbox.to_ee_rectangle()
        # Based on testing, this kernel reduces some noise while maintaining range of values
        kernel = ee.Kernel.gaussian(
            radius=3, sigma=0.25, units='pixels', normalize=True
        )
        alos_dsm_ic = ee.ImageCollection(
            alos_dsm
            .filterBounds(ee_rectangle['ee_geometry'])
            .select('DSM')
            .map(lambda x:
                 set_resampling_for_continuous_raster(x,
                                                      resampling_method,
                                                      spatial_resolution,
                                                      DEFAULT_SPATIAL_RESOLUTION,
                                                      kernel,
                                                      ee_rectangle['crs']
                                                      )
                 )
            .mean()
        )

        data = get_image_collection(
            alos_dsm_ic,
            ee_rectangle,
            spatial_resolution,
            "ALOS DSM"
        ).DSM

        # Round value to reduce variability
        rounded_data = data.round(2)

        return rounded_data
