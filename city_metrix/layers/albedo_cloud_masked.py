import ee

from city_metrix.metrix_model import (
    GeoExtent,
    Layer,
    get_image_collection,
    set_resampling_for_continuous_raster,
    validate_raster_resampling_method,
)
from city_metrix.metrix_tools import align_raster_array

from ..constants import GTIFF_FILE_EXTENSION
from ..metrix_dao import extract_bbox_aoi
from .albedo import get_albedo_default_date_range
from .world_pop import WorldPop

DEFAULT_SPATIAL_RESOLUTION = 10
DEFAULT_RESAMPLING_METHOD = "bilinear"


class AlbedoCloudMasked(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["zonal_stats"]
    MINOR_NAMING_ATTS = None
    PROCESSING_TILE_SIDE_M = 5000

    """
    Attributes:
        start_date: starting date for data retrieval
        end_date: ending date for data retrieval
        zonal_stats: use 'mean' or 'median' for albedo zonal stats
    """

    def __init__(self, start_date:str=None, end_date:str=None, index_aggregation=True, zonal_stats='median', **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.zonal_stats = zonal_stats
        self.index_aggregation = index_aggregation

    def get_masked_s2_collection(self, bbox_ee, start_date, end_date):
        CLEAR_THRESHOLD = 0.60

        S2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        S2CS = ee.ImageCollection("GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED")

        # Cloud score+
        S2filtered = (
            S2.filterBounds(bbox_ee["ee_geometry"])
            .filterDate(start_date, end_date)
            .linkCollection(S2CS, ["cs"])
            .map(lambda img: img.updateMask(img.select("cs").gte(CLEAR_THRESHOLD)).divide(10000))
        )

        return S2filtered

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method: str = DEFAULT_RESAMPLING_METHOD):
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)

        buffered_utm_bbox = bbox.buffer_utm_bbox(10)
        ee_rectangle  = buffered_utm_bbox.to_ee_rectangle()

        if self.start_date is None or self.end_date is None:
            self.start_date, self.end_date = get_albedo_default_date_range(bbox)
            print("Date range was not specified for Albedo, so auto-setting to previous-year summer months as appropriate for hemisphere.")

        # calculate albedo for images
        # weights derived from
        # S. Bonafoni and A. Sekertekin, "Albedo Retrieval From Sentinel-2 by New Narrow-to-Broadband Conversion Coefficients," in IEEE Geoscience and Remote Sensing Letters, vol. 17, no. 9, pp. 1618-1622, Sept. 2020, doi: 10.1109/LGRS.2020.2967085.
        def calc_s2_albedo(image):
            S2_ALBEDO_EQN = "((B*Bw)+(G*Gw)+(R*Rw)+(NIR*NIRw)+(SWIR1*SWIR1w)+(SWIR2*SWIR2w))"
            config = {
                "Bw": 0.2266,
                "Gw": 0.1236,
                "Rw": 0.1573,
                "NIRw": 0.3417,
                "SWIR1w": 0.1170,
                "SWIR2w": 0.0338,
                "B": image.select("B2"),
                "G": image.select("B3"),
                "R": image.select("B4"),
                "NIR": image.select("B8"),
                "SWIR1": image.select("B11"),
                "SWIR2": image.select("B12"),
            }

            albedo = image.expression(S2_ALBEDO_EQN, config).double().rename("albedo")

            return albedo

        # Get masked S2 collection
        S2filtered = self.get_masked_s2_collection(ee_rectangle, self.start_date, self.end_date)
        # Add albedo
        S2albedo = S2filtered.map(calc_s2_albedo).select("albedo")

        # Median/Mean albedo
        kernel_convolution = None
        if self.zonal_stats == 'mean':
            albedo_zonal = S2albedo.map(
                lambda x: set_resampling_for_continuous_raster(
                    x,
                    resampling_method,
                    spatial_resolution,
                    DEFAULT_SPATIAL_RESOLUTION,
                    kernel_convolution,
                    ee_rectangle["crs"],
                )
            ).reduce(ee.Reducer.mean()).rename('albedo_zonal')
        elif self.zonal_stats == 'median':
            albedo_zonal = S2albedo.map(
                lambda x: set_resampling_for_continuous_raster(
                    x,
                    resampling_method,
                    spatial_resolution,
                    DEFAULT_SPATIAL_RESOLUTION,
                    kernel_convolution,
                    ee_rectangle["crs"],
                )
            ).reduce(ee.Reducer.median()).rename('albedo_zonal')
        else:
            raise Exception("invalid zonal stats method, should be 'mean' or 'median'")

        albedo_zonal_ic = ee.ImageCollection(albedo_zonal)
        data = get_image_collection(
            albedo_zonal_ic,
            ee_rectangle,
            spatial_resolution,
            "cloud masked albedo",
        ).albedo_zonal

        # clamping all values ≥ 1 down to exactly 1, and leaving values < 1 untouched
        result_data = data.where(data < 1, 1)

        # Trim back to original AOI
        result_data = extract_bbox_aoi(result_data, bbox)
        if self.index_aggregation:
            wp_array =  WorldPop().get_data(bbox)
            return align_raster_array(data, wp_array)

        return result_data
