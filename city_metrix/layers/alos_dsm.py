import ee
import xee
import xarray as xr


from .layer import Layer, get_image_collection, set_resampling_for_continuous_raster


class AlosDSM(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
        resampling_method: interpolation method used by Google Earth Engine. Default is 'bilinear'. All options are: ('bilinear', 'bicubic', None).
    """

    def __init__(self, spatial_resolution:int=30, resampling_method:str='bilinear', **kwargs):
        super().__init__(**kwargs)
        self.spatial_resolution = spatial_resolution
        self.resampling_method = resampling_method

    def get_data(self, bbox: tuple[float, float, float, float]):
        alos_dsm = ee.ImageCollection("JAXA/ALOS/AW3D30/V3_2")

        alos_dsm_ic = ee.ImageCollection(
            alos_dsm
            .filterBounds(ee.Geometry.BBox(*bbox))
            .select('DSM')
            .map(lambda x:
                 set_resampling_for_continuous_raster(x,
                                                      self.resampling_method,
                                                      self.spatial_resolution,
                                                      bbox
                                                      )
                 )
            .mean()
        )


        data = get_image_collection(
            alos_dsm_ic,
            bbox,
            self.spatial_resolution,
            "ALOS DSM"
        ).DSM

        return data
