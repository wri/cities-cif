import ee

from .layer import Layer, get_image_collection, set_bilinear_resampling

class LandSurfaceTemperature(Layer):
    """
    Attributes:
        start_date: starting date for data retrieval
        end_date: ending date for data retrieval
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, start_date="2013-01-01", end_date="2023-01-01", spatial_resolution=30, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        def cloud_mask(image):
            qa = image.select('QA_PIXEL')

            mask = qa.bitwiseAnd(1 << 3).Or(qa.bitwiseAnd(1 << 4))
            return image.updateMask(mask.Not())

        def apply_scale_factors(image):
            thermal_band = image.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15)
            return thermal_band

        l8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")

        l8_st = (l8
                 .select('ST_B10', 'QA_PIXEL')
                 .filter(ee.Filter.date(self.start_date, self.end_date))
                 .filterBounds(ee.Geometry.BBox(*bbox))
                 .map(cloud_mask)
                 .map(apply_scale_factors)
                 .map(set_bilinear_resampling)
                 .reduce(ee.Reducer.mean())
                 )

        l8_st_ic = ee.ImageCollection(l8_st)
        data = get_image_collection(
            l8_st_ic,
            bbox,
            self.spatial_resolution,
            "LST"
        ).ST_B10_mean

        return data
