import ee

from city_metrix.metrix_model import (Layer, get_image_collection, set_resampling_for_continuous_raster,
                                      validate_raster_resampling_method, GeoExtent)
from ..metrix_dao import extract_bbox_aoi
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 30
DEFAULT_RESAMPLING_METHOD = 'bilinear'

class FabDEM(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None
    PROCESSING_TILE_SIDE_M = 5000
    # tile-size testing for Teresina
    # 1. no tiling = 6:49 min (run mode)
    # 2. 10k = 19:00 (debug mode)
    # 3. 20k = 8:17 (run mode)
    # 4. 30k = 7:41 (run mode) no tmp directory observed since city area is smaller, so same as no tiling

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

        buffered_utm_bbox = bbox.buffer_utm_bbox(10)
        ee_rectangle  = buffered_utm_bbox.to_ee_rectangle()

        fab_dem = ee.ImageCollection("projects/sat-io/open-datasets/FABDEM")

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

        # Trim back to original AOI
        bbox_results = extract_bbox_aoi(rounded_data, bbox)

        return bbox_results
