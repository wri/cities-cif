import ee

from city_metrix.metrix_model import Layer, get_image_collection, GeoExtent
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 10

class NdwiSentinel2(Layer):
    """"
    NDWI = Sentinel-2 Normalized Difference Water Index
    return: a rioxarray-format DataArray
    Author of associated Jupyter notebook: EricMackres@wri.org
    Notebook: https://github.com/wri/cities-cities4forests-indicators/blob/dev-eric/scripts/extract-VegetationCover.ipynb
    Reference: McFeeters (1996) https://doi.org/10.1080/01431169608948714
    """
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        year: The satellite imaging year.
    """
    def __init__(self, year=2021, **kwargs):
        super().__init__(**kwargs)
        self.year = year

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        if self.year is None:
            raise Exception('NdwiSentinel2.get_data() requires a year value')

        start_date = "%s-01-01" % self.year
        end_date = "%s-12-31" % self.year

        # Compute NDWI for each image
        def calculate_ndwi(image):
            ndwi = (image
                    .normalizedDifference(['B3', 'B8'])
                    .rename('NDWI'))
            return image.addBands(ndwi)

        s2 = ee.ImageCollection("COPERNICUS/S2_HARMONIZED")

        ee_rectangle  = bbox.to_ee_rectangle()
        ndwi = (s2
                .filterBounds(ee_rectangle['ee_geometry'])
                .filterDate(start_date, end_date)
                .map(calculate_ndwi)
                .select('NDWI')
                 )

        ndwi_mosaic = ndwi.qualityMosaic('NDWI')

        ndwi_mosaic_ic = ee.ImageCollection(ndwi_mosaic)
        ndwi_data = get_image_collection(
            ndwi_mosaic_ic,
            ee_rectangle,
            spatial_resolution,
            "NDWI"
        ).NDWI

        return ndwi_data
