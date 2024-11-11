import ee
import xarray
from dask.diagnostics import ProgressBar

from .layer import Layer, get_utm_zone_epsg, get_image_collection


class Albedo(Layer):
    """
    Attributes:
        start_date: starting date for data retrieval
        end_date: ending date for data retrieval
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
        threshold: threshold value for filtering the retrieval
    """
    MAX_CLOUD_PROB = 30
    S2_ALBEDO_EQN = '((B*Bw)+(G*Gw)+(R*Rw)+(NIR*NIRw)+(SWIR1*SWIR1w)+(SWIR2*SWIR2w))'

    def __init__(self, start_date="2021-01-01", end_date="2022-01-01", spatial_resolution=10, threshold=None, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.spatial_resolution = spatial_resolution
        self.threshold = threshold

    # get cloudmasked image collection
    def mask_clouds_and_rescale(self, im):
        clouds = ee.Image(im.get('cloud_mask')).select('probability')
        return im.updateMask(clouds.lt(self.MAX_CLOUD_PROB)).divide(10000)

    def get_masked_s2_collection(self, roi, start, end):
        criteria = (ee.Filter.And(
            ee.Filter.date(start, end),
            ee.Filter.bounds(roi)
        ))
        # .select('B2','B3','B4','B8','B11','B12')
        s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filter(criteria)
        s2c = ee.ImageCollection("COPERNICUS/S2_CLOUD_PROBABILITY").filter(criteria)
        s2_with_clouds = (ee.Join.saveFirst('cloud_mask').apply(**{
            'primary': ee.ImageCollection(s2),
            'secondary': ee.ImageCollection(s2c),
            'condition': ee.Filter.equals(**{'leftField': 'system:index', 'rightField': 'system:index'})
        }))

        # s2_with_clouds=s2_with_clouds.limit(image_limit,'nb_cloudy_pixels')
        s2_with_clouds = ee.ImageCollection(s2_with_clouds).map(
            self.mask_clouds_and_rescale)  # .limit(image_limit,'CLOUDY_PIXEL_PERCENTAGE')
        return ee.ImageCollection(s2_with_clouds)

    def get_data(self, bbox):
        # calculate albedo for images

        # weights derived from
        # S. Bonafoni and A. Sekertekin, "Albedo Retrieval From Sentinel-2 by New Narrow-to-Broadband Conversion Coefficients," in IEEE Geoscience and Remote Sensing Letters, vol. 17, no. 9, pp. 1618-1622, Sept. 2020, doi: 10.1109/LGRS.2020.2967085.
        def calc_s2_albedo(image):
            config = {
                'Bw': 0.2266,
                'Gw': 0.1236,
                'Rw': 0.1573,
                'NIRw': 0.3417,
                'SWIR1w': 0.1170,
                'SWIR2w': 0.0338,
                'B': image.select('B2'),
                'G': image.select('B3'),
                'R': image.select('B4'),
                'NIR': image.select('B8'),
                'SWIR1': image.select('B11'),
                'SWIR2': image.select('B12')
            }
            return image.expression(self.S2_ALBEDO_EQN, config).double().rename('albedo')

        # S2 MOSAIC AND ALBEDO
        dataset = self.get_masked_s2_collection(ee.Geometry.BBox(*bbox), self.start_date, self.end_date)
        s2_albedo = dataset.map(calc_s2_albedo)
        albedo_mean = s2_albedo.reduce(ee.Reducer.mean())

        data = (get_image_collection(ee.ImageCollection(albedo_mean), bbox, self.spatial_resolution, "albedo").albedo_mean)

        if self.threshold is not None:
            return data.where(data < self.threshold)

        return data
