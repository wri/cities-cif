import ee
import xee
import xarray as xr

from .layer import Layer, get_image_collection, set_resampling_for_continuous_raster, validate_raster_resampling_method
from .layer_geometry import LayerBbox

DEFAULT_SPATIAL_RESOLUTION = 30
DEFAULT_RESAMPLING_METHOD = 'bilinear'

class AlosDSM(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
        resampling_method: interpolation method used by Google Earth Engine. Default is 'bilinear'. All options are: ('bilinear', 'bicubic', None).
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox: LayerBbox, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method:str=DEFAULT_RESAMPLING_METHOD):

        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)

        alos_dsm = ee.ImageCollection("JAXA/ALOS/AW3D30/V3_2")

        ee_rectangle  = bbox.to_ee_rectangle(output_as='utm')
        alos_dsm_ic = ee.ImageCollection(
            alos_dsm
            .filterBounds(ee_rectangle['ee_geometry'])
            .select('DSM')
            .map(lambda x:
                 set_resampling_for_continuous_raster(x,
                                                      resampling_method,
                                                      spatial_resolution,
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

        return data
