from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_utm_zone_epsg, get_image_collection


class HeightAboveNearestDrainage(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
        river_head: number of river head threshold cells
    """

    def __init__(self, spatial_resolution=30, river_head=1000, **kwargs):
        super().__init__(**kwargs)
        self.spatial_resolution = spatial_resolution
        self.river_head = river_head

    def get_data(self, bbox):
        if self.spatial_resolution == 30 and self.river_head == 100:
            hand = ee.ImageCollection('users/gena/global-hand/hand-100')
            # smoothen HAND a bit, scale varies a little in the tiles
            hand = hand.mosaic().focal_mean(0.1)
        elif self.spatial_resolution == 30:
            hand = ee.Image(f'users/gena/GlobalHAND/30m/hand-{self.river_head}')
            # smoothen HAND a bit, scale varies a little in the tiles
            hand = hand.focal_mean(0.1)
        elif self.spatial_resolution == 90:
            hand = ee.Image(f'users/gena/GlobalHAND/90m-global/hand-{self.river_head}')
            # smoothen HAND a bit, scale varies a little in the tiles
            hand = hand.focal_mean(0.1)

        # MOD44W.005 Land Water Mask Derived From MODIS and SRTM
        swbd = ee.Image('MODIS/MOD44W/MOD44W_005_2000_02_24').select('water_mask')
        swbdMask = swbd.unmask().Not().focal_median(1)

        thresh = 1
        HANDthresh = hand.lte(thresh).focal_max(1).focal_mode(2, 'circle', 'pixels', 5).mask(swbdMask)
        HANDthresh = HANDthresh.mask(HANDthresh)

        data = get_image_collection(ee.ImageCollection(HANDthresh), bbox, self.spatial_resolution, "height above nearest drainage")

        return data.b1
