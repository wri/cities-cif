import ee

from .layer import Layer, get_image_collection, set_bilinear_resampling


class AlosDSM(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, spatial_resolution=30, **kwargs):
        super().__init__(**kwargs)
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        alos_dsm = ee.ImageCollection("JAXA/ALOS/AW3D30/V3_2")

        alos_dsm_ic = ee.ImageCollection(alos_dsm
                                         .filterBounds(ee.Geometry.BBox(*bbox))
                                         .map(set_bilinear_resampling)
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
