import ee

from city_metrix.metrix_model import Layer, get_image_collection, GeoExtent
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 1113.1949  # 10 degrees of earth circumference
SUPPORTED_YEARS = [2010, 2012, 2014, 2016, 2018, 2020, 2022]

class AcagPM2p5(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["return_above"]
    """
    Attributes:
        year: only available year is 2022
        return_above:
    """
    def __init__(self, year=2022, return_above=0, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.return_above = return_above

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        acag_data = ee.Image(f'projects/wri-datalab/cities/aq/acag_annual_pm2p5_{self.year}')

        ee_rectangle  = bbox.to_ee_rectangle()
        data = get_image_collection(
            ee.ImageCollection(acag_data),
            ee_rectangle,
            spatial_resolution,
            "mean pm2.5 concentration"
        ).b1

        data = data.where(data >= self.return_above)

        return data
