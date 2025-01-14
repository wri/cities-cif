import ee
from xrspatial import slope

from .layer import Layer
from .nasa_dem import NasaDEM


class HighSlope(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
        resampling_method: interpolation method used by Google Earth Engine. Default is 'bilinear'. All options are: ('bilinear', 'bicubic', None).
    """

    def __init__(self, spatial_resolution:int=30, resampling_method:str='bilinear', slope_threshold:int=10, **kwargs):
        super().__init__(**kwargs)
        self.spatial_resolution = spatial_resolution
        self.resampling_method = resampling_method
        self.slope_threshold = slope_threshold

    def get_data(self, bbox: tuple[float, float, float, float]):
        nasa_dem = NasaDEM(spatial_resolution=self.spatial_resolution,
                           resampling_method=self.resampling_method).get_data(bbox)

        slope_data = slope(nasa_dem)
        steep_slope = slope_data.where(slope_data >= self.slope_threshold)

        return steep_slope
