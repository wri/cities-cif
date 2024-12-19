import ee
import xee
import xarray as xr

from .layer import Layer, get_image_collection, set_resampling_method


class NasaDEM(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
        resampling_method: interpolation method used by Google Earth Engine. Default is 'bilinear'. All options are: ('bilinear', 'bicubic', None).
    """

    def __init__(self, spatial_resolution=30, resampling_method='bilinear', **kwargs):
        super().__init__(**kwargs)
        self.spatial_resolution = spatial_resolution
        self.resampling_method = resampling_method

    def get_data(self, bbox):
        nasa_dem = ee.Image("NASA/NASADEM_HGT/001")

        if self.resampling_method is not None:
            nasa_dem_elev = (ee.ImageCollection(nasa_dem)
                             .filterBounds(ee.Geometry.BBox(*bbox))
                             .map(lambda x: set_resampling_method(x, self.resampling_method), )
                             .select('elevation')
                             .mean()
                             )
        else:
            nasa_dem_elev = (ee.ImageCollection(nasa_dem)
                             .filterBounds(ee.Geometry.BBox(*bbox))
                             .select('elevation')
                             .mean()
                             )

        nasa_dem_elev_ic = ee.ImageCollection(nasa_dem_elev)
        data = get_image_collection(
            nasa_dem_elev_ic,
            bbox,
            self.spatial_resolution,
            "NASA DEM"
        ).elevation

        return data
