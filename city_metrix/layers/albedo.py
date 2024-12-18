import ee

from .layer import Layer, get_image_collection

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
    
    ## METHODS
    ## get cloudmasked image collection
    def mask_and_count_clouds(self, s2wc, geom):
        s2wc = ee.Image(s2wc)
        geom = ee.Geometry(geom.geometry())
        is_cloud = (ee.Image(s2wc.get('cloud_mask'))
                    .gt(self.MAX_CLOUD_PROB)
                    .rename('is_cloud')
                    )

        nb_cloudy_pixels = is_cloud.reduceRegion(
            reducer=ee.Reducer.sum().unweighted(),
            geometry=geom,
            scale=self.spatial_resolution,
            maxPixels=1e9
        )
        mask = (s2wc
                .updateMask(is_cloud.eq(0))
                .set('nb_cloudy_pixels',nb_cloudy_pixels.getNumber('is_cloud'))
                .divide(10000)
                )

        return mask

    def mask_clouds_and_rescale(self, im):
        clouds = ee.Image(im.get('cloud_mask')
                          ).select('probability')
        mask = im.updateMask(clouds
                             .lt(self.MAX_CLOUD_PROB)
                             ).divide(10000)

        return mask

    def get_masked_s2_collection(self, roi, start, end):
        criteria = (ee.Filter.And(
            ee.Filter.date(start, end),
            ee.Filter.bounds(roi)
        ))
        s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filter(criteria)  # .select('B2','B3','B4','B8','B11','B12')
        s2c = ee.ImageCollection("COPERNICUS/S2_CLOUD_PROBABILITY").filter(criteria)
        s2_with_clouds = (
            ee.Join.saveFirst('cloud_mask')
            .apply(**{
                'primary': ee.ImageCollection(s2),
                'secondary': ee.ImageCollection(s2c),
                'condition': ee.Filter.equals(**{'leftField': 'system:index', 'rightField': 'system:index'})
            })
        )

        def _mcc(im):
            return self.mask_and_count_clouds(im, roi)
            # s2_with_clouds=ee.ImageCollection(s2_with_clouds).map(_mcc)

        # s2_with_clouds=s2_with_clouds.limit(image_limit,'nb_cloudy_pixels')
        s2_with_clouds = (ee.ImageCollection(s2_with_clouds)
                          .map(self.mask_clouds_and_rescale)
                          )  # .limit(image_limit,'CLOUDY_PIXEL_PERCENTAGE')

        s2_with_clouds_ic = ee.ImageCollection(s2_with_clouds)

        return s2_with_clouds_ic

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

            albedo = image.expression(self.S2_ALBEDO_EQN, config).double().rename('albedo')

            return albedo

        # S2 MOSAIC AND ALBEDO
        dataset = self.get_masked_s2_collection(ee.Geometry.BBox(*bbox), self.start_date, self.end_date)
        s2_albedo = dataset.map(calc_s2_albedo)
        albedo_mean = s2_albedo.reduce(ee.Reducer.mean())

        albedo_mean_ic = ee.ImageCollection(albedo_mean)
        data = get_image_collection(
            albedo_mean_ic,
            bbox,
            self.spatial_resolution,
            "albedo"
        ).albedo_mean

        if self.threshold is not None:
            return data.where(data < self.threshold)

        return data
