import ee

from city_metrix.metrix_model import (Layer, get_image_collection, set_resampling_for_continuous_raster,
                                      validate_raster_resampling_method, GeoExtent)
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 30
DEFAULT_RESAMPLING_METHOD = 'bilinear'

class FabDEM(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
        resampling_method: interpolation method used by Google Earth Engine. Valid options: ('bilinear', 'bicubic', 'nearest').
    """
    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method:str=DEFAULT_RESAMPLING_METHOD):
        
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)

        fab_dem = ee.ImageCollection("projects/sat-io/open-datasets/FABDEM")

        ee_rectangle  = bbox.to_ee_rectangle()

        # Based on testing, this kernel reduces some noise while maintaining range of values
        kernel = ee.Kernel.gaussian(
            radius=3, sigma=1, units='pixels', normalize=True
        )
        fab_dem_elev = (ee.ImageCollection(fab_dem)
                         .filterBounds(ee_rectangle['ee_geometry'])
                         .select('b1')
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

        fab_dem_elev_ic = ee.ImageCollection(fab_dem_elev)
        data = get_image_collection(
            fab_dem_elev_ic,
            ee_rectangle,
            spatial_resolution,
            "FAB DEM"
        ).b1

        # Round value to reduce variability
        rounded_data = data.round(2)

        return rounded_data
