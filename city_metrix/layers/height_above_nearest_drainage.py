import ee

from city_metrix.metrix_model import Layer, get_image_collection, GeoExtent
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 30

class HeightAboveNearestDrainage(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["river_head"]
    MINOR_NAMING_ATTS = ["thresh"]
    PROCESSING_TILE_SIDE_M = 5000

    """
    Attributes:
        river_head: number of river head threshold cells
                    default is 1000, other options - 100, 5000
        thresh: flow accumulation threshold, default is 1
    """
    def __init__(self, river_head=1000, thresh=1, nanval=None, **kwargs):
        super().__init__(**kwargs)
        self.river_head = river_head
        self.thresh = thresh
        self.nanval = nanval

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        if spatial_resolution not in [30,90]:
            raise Exception(f'spatial_resolution of {spatial_resolution} is currently not supported.')

        if spatial_resolution == 30 and self.river_head == 100:
            hand = ee.ImageCollection('users/gena/global-hand/hand-100')
            # smoothen HAND a bit, scale varies a little in the tiles
            hand = hand.mosaic().focal_mean(0.1)
        elif spatial_resolution == 30:
            hand = ee.Image(f'users/gena/GlobalHAND/30m/hand-{self.river_head}')
            # smoothen HAND a bit, scale varies a little in the tiles
            hand = hand.focal_mean(0.1)
        elif spatial_resolution == 90:
            hand = ee.Image(f'users/gena/GlobalHAND/90m-global/hand-{self.river_head}')
            # smoothen HAND a bit, scale varies a little in the tiles
            hand = hand.focal_mean(0.1)

        # MOD44W.005 Land Water Mask Derived From MODIS and SRTM
        swbd = ee.Image('MODIS/MOD44W/MOD44W_005_2000_02_24').select('water_mask')
        swbdMask = swbd.unmask().Not().focal_median(1)

        thresh = self.thresh
        HANDthresh = hand.lte(thresh).focal_max(1).focal_mode(2, 'circle', 'pixels', 5).mask(swbdMask)
        HANDthresh = HANDthresh.mask(HANDthresh)

        ee_rectangle = bbox.to_ee_rectangle()
        data = get_image_collection(
            ee.ImageCollection(HANDthresh),
            ee_rectangle,
            spatial_resolution,
            "height above nearest drainage"
        ).b1

        if self.nanval is not None:
            data = data.fillna(self.nanval)

        return data
