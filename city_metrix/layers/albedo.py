import ee

from city_metrix.metrix_model import (Layer, get_image_collection, set_resampling_for_continuous_raster,
                                      validate_raster_resampling_method, GeoExtent)
from ..constants import GTIFF_FILE_EXTENSION
from datetime import datetime, timedelta

DEFAULT_SPATIAL_RESOLUTION = 10
DEFAULT_RESAMPLING_METHOD = 'bilinear'

class Albedo(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["threshold"]
    MAX_CLOUD_PROB = 30
    S2_ALBEDO_EQN = '((B*Bw)+(G*Gw)+(R*Rw)+(NIR*NIRw)+(SWIR1*SWIR1w)+(SWIR2*SWIR2w))'

    """
    Attributes:
        start_date: starting date for data retrieval
        end_date: ending date for data retrieval
        threshold: threshold value for filtering the retrieval
    """
    def __init__(self, start_date:str='2021-01-01', end_date:str='2022-01-01', threshold=None, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
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

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method:str=DEFAULT_RESAMPLING_METHOD):
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)

        if self.start_date is None or self.end_date is None:
            self.start_date, self.end_date = get_albedo_default_date_range(bbox)
            print("Date range was not specified for Albedo, so auto-setting to previous-year summer months as appropriate for hemisphere.")

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
        ee_rectangle = bbox.to_ee_rectangle()
        dataset = self.get_masked_s2_collection(ee_rectangle['ee_geometry'], self.start_date, self.end_date)
        s2_albedo = dataset.map(calc_s2_albedo)

        kernel_convolution = None
        albedo_mean = (s2_albedo
                       .map(lambda x:
                                    set_resampling_for_continuous_raster(x,
                                                                         resampling_method,
                                                                         spatial_resolution,
                                                                         DEFAULT_SPATIAL_RESOLUTION,
                                                                         kernel_convolution,
                                                                         ee_rectangle['crs']
                                                                         )
                            )
                       .reduce(ee.Reducer.mean())
                       )

        albedo_mean_ic = ee.ImageCollection(albedo_mean)
        data = get_image_collection(
            albedo_mean_ic,
            ee_rectangle,
            spatial_resolution,
            "albedo"
        ).albedo_mean

        if self.threshold is not None:
            return data.where(data < self.threshold)

        return data

"""
Determines last day of February since the date varies for leap and non-leap years.
"""
def last_date_of_february(year):
    march_first = datetime(year, 3, 1)
    last_february_date = march_first - timedelta(days=1)
    return last_february_date.strftime("%Y-%m-%d")

"""
Function used by both Albedo and AlbedoCloudMasked layers to determine 3-month time windows for summer in the
northern and southern hemispheres.
"""
def get_albedo_default_date_range(bbox: GeoExtent):
    geo_bbox = bbox.as_geographic_bbox()
    aoi_centroid = geo_bbox.centroid
    this_year = datetime.now().year
    one_year_ago_offset = this_year - 1
    two_years_ago_offset = this_year - 2
    if aoi_centroid.y >= 0:
        # Get summer months for northern-hemisphere in middle of calendar year
        start_date = f"{one_year_ago_offset}-06-01"
        end_date = f"{one_year_ago_offset}-08-31"
    else:
        # Get summer months for southern-hemisphere at start of the previous calendar year
        start_date = f"{two_years_ago_offset}-12-01"
        end_date = last_date_of_february(one_year_ago_offset)

    return start_date, end_date