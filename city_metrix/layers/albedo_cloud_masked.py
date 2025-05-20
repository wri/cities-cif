import ee

from city_metrix.metrix_model import (Layer, get_image_collection, set_resampling_for_continuous_raster,
                                      validate_raster_resampling_method, GeoExtent)
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 10
DEFAULT_RESAMPLING_METHOD = "bilinear"


class AlbedoCloudMasked(Layer):
    GEOSPATIAL_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None
    S2_ALBEDO_EQN = "((B*Bw)+(G*Gw)+(R*Rw)+(NIR*NIRw)+(SWIR1*SWIR1w)+(SWIR2*SWIR2w))"
    CLEAR_THRESHOLD = 0.60

    """
    Attributes:
        start_date: starting date for data retrieval
        end_date: ending date for data retrieval
    """

    def __init__(self, start_date="2023-06-01", end_date="2023-08-31", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method: str = DEFAULT_RESAMPLING_METHOD):
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)

        # calculate albedo for images
        # weights derived from
        # S. Bonafoni and A. Sekertekin, "Albedo Retrieval From Sentinel-2 by New Narrow-to-Broadband Conversion Coefficients," in IEEE Geoscience and Remote Sensing Letters, vol. 17, no. 9, pp. 1618-1622, Sept. 2020, doi: 10.1109/LGRS.2020.2967085.
        def calc_s2_albedo(image):
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

            albedo = image.expression(self.S2_ALBEDO_EQN, config).double().rename("albedo")

            return albedo

        s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        s2cs = ee.ImageCollection("GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED")

        ee_rectangle = bbox.to_ee_rectangle()
        # Cloud score+
        s2_filtered = (
            s2.filterBounds(ee_rectangle["ee_geometry"])
            .filterDate(self.start_date, self.end_date)
            .linkCollection(s2cs, linkedBands=["cs"])
        )
        s2_filtered = s2_filtered.map(
            lambda img: img.updateMask(
                img.select("cs").gte(self.CLEAR_THRESHOLD)
            ).divide(10000)
        )
        # Add albedo
        s2_albedo = s2_filtered.map(calc_s2_albedo).select("albedo")

        # Median albedo
        kernel_convolution = None
        albedo_median = s2_albedo.map(
            lambda x: set_resampling_for_continuous_raster(
                x,
                resampling_method,
                spatial_resolution,
                DEFAULT_SPATIAL_RESOLUTION,
                kernel_convolution,
                ee_rectangle["crs"],
            )
        ).reduce(ee.Reducer.median())

        albedo_median_ic = ee.ImageCollection(albedo_median)
        data = get_image_collection(
            albedo_median_ic, 
            ee_rectangle, 
            spatial_resolution, 
            "albedo"
        ).albedo_median

        # clamping all values ≥ 1 down to exactly 1, and leaving values < 1 untouched
        data = data.where(data < 1, 1)

        return data
