import ee

from .layer import Layer, get_image_collection, set_resampling_method


class AlosDSM(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
        resampling_method: interpolation method used by Google Earth Engine. AlosDSM default is 'bilinear'. All options are: ('bilinear', 'bicubic', None).
    """

    def __init__(self, spatial_resolution=30, resampling_method='bilinear', **kwargs):
        super().__init__(**kwargs)
        self.spatial_resolution = spatial_resolution
        self.resampling_method = resampling_method

    def get_data(self, bbox):
        alos_dsm = ee.ImageCollection("JAXA/ALOS/AW3D30/V3_2")

        if self.resampling_method is not None:
            alos_dsm_ic = ee.ImageCollection(
                alos_dsm
                .filterBounds(ee.Geometry.BBox(*bbox))
                .map(lambda x: set_resampling_method(x, self.resampling_method), )
                .select('DSM')
                .mean()
            )
        else:
            alos_dsm_ic = ee.ImageCollection(
                alos_dsm
                .filterBounds(ee.Geometry.BBox(*bbox))
                .select('DSM')
                .mean()
            )

        data = get_image_collection(
            alos_dsm_ic,
            bbox,
            self.spatial_resolution,
            "ALOS DSM"
        ).DSM

        return data
