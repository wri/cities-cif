import xarray as xr
import numpy as np
import ee
from scipy.ndimage import distance_transform_edt

from .layer import Layer, get_image_collection
from .height_above_nearest_drainage import HeightAboveNearestDrainage


class RiparianAreas(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
                            default is 30, other options - 90
        river_head: number of river head threshold cells
                    default is 1000, other options - 100, 5000
        thresh: flow accumuation threshold, default is 0
    """

    def __init__(self, spatial_resolution=30, river_head=1000, thresh=0, **kwargs):
        super().__init__(**kwargs)
        self.spatial_resolution = spatial_resolution
        self.river_head = river_head
        self.thresh = thresh

    def get_data(self, bbox):
        # read HAND data to generate drainage paths
        hand = HeightAboveNearestDrainage(spatial_resolution=self.spatial_resolution, river_head=self.river_head, thresh=self.thresh).get_data(bbox)

        # Read surface water occurance
        water = ee.Image('JRC/GSW1_3/GlobalSurfaceWater').select(['occurrence']).gte(50)
        water_da = get_image_collection(
            ee.ImageCollection(water),
            bbox,
            self.spatial_resolution,
            "water"
        ).occurrence

        combWater = np.maximum(hand.fillna(0), water_da.fillna(0)) > 0
        combWater = combWater.fillna(False)

        # Buffer waterways by riparian zone definitions
        distance_arr = xr.apply_ufunc(
            distance_transform_edt,
            ~combWater,  # True where not-water
            input_core_dims=[('y', 'x')],
            output_core_dims=[('y', 'x')],
            dask='parallelized',
            kwargs={'sampling': self.spatial_resolution}
        )

        halfpixel = self.spatial_resolution * 0.5
        # https://doi.org/10.1016/j.jenvman.2019.109391
        distance_200 = distance_arr.where(distance_arr <= 200)
        nutrientBuffer = (distance_200 <= (3.0 - halfpixel))
        floraBuffer = (distance_200 <= (24.0 - halfpixel))
        birdBuffer = (distance_200 <= (144.0 - halfpixel))

        riparianMask = birdBuffer

        return riparianMask
