import xarray as xr
import numpy as np
import ee
from scipy.ndimage import distance_transform_edt

from .layer import Layer, get_image_collection
from .height_above_nearest_drainage import HeightAboveNearestDrainage
from .layer_geometry import GeoExtent, retrieve_cached_city_data
from .layer_tools import build_s3_names

DEFAULT_SPATIAL_RESOLUTION = 30

class RiparianAreas(Layer):
    OUTPUT_FILE_FORMAT = 'tif'

    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
                            default is 30, other options - 90
        river_head: number of river head threshold cells
                    default is 1000, other options - 100, 5000
        thresh: flow accumuation threshold, default is 0
    """
    def __init__(self, river_head=1000, thresh=0, **kwargs):
        super().__init__(**kwargs)
        self.river_head = river_head
        self.thresh = thresh

    def get_layer_names(self):
        minor_qualifier = {"river_head": self.river_head,
                           "thresh": self.thresh}

        layer_name, layer_id, file_format = build_s3_names(self, None, minor_qualifier)
        return layer_name, layer_id, file_format

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_s3_cache_retrieval=False):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        layer_name, layer_id, file_format = self.get_layer_names()
        retrieved_cached_data = retrieve_cached_city_data(bbox, layer_name, layer_id, file_format, allow_s3_cache_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        # read HAND data to generate drainage paths
        hand = HeightAboveNearestDrainage(river_head=self.river_head, thresh=self.thresh).get_data(bbox, spatial_resolution=spatial_resolution)

        # Read surface water occurance
        water = ee.Image('JRC/GSW1_3/GlobalSurfaceWater').select(['occurrence']).gte(50)
        ee_rectangle = bbox.to_ee_rectangle()
        water_da = get_image_collection(
            ee.ImageCollection(water),
            ee_rectangle,
            spatial_resolution,
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
            kwargs={'sampling': spatial_resolution}
        )

        halfpixel = spatial_resolution * 0.5
        # https://doi.org/10.1016/j.jenvman.2019.109391
        distance_200 = distance_arr.where(distance_arr <= 200)
        nutrientBuffer = (distance_200 <= (3.0 - halfpixel))
        floraBuffer = (distance_200 <= (24.0 - halfpixel))
        birdBuffer = (distance_200 <= (144.0 - halfpixel))

        # get riparian mask
        data = birdBuffer.rio.write_crs(bbox.as_utm_bbox().crs)

        return data
