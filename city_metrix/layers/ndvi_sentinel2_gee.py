import ee
from tools.xarray_tools import convert_ratio_to_percentage
from .layer import Layer, get_image_collection

class NdviSentinel2(Layer):
    """"
    NDVI = Sentinel-2 Normalized Difference Vegetation Index
    param: year: The satellite imaging year.
    return: a rioxarray-format DataArray
    Author of associated Jupyter notebook: Ted.Wong@wri.org
    Notebook: https://github.com/wri/cities-cities4forests-indicators/blob/dev-eric/scripts/extract-VegetationCover.ipynb
    Reference: https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index
    """
    def __init__(self, year=None, **kwargs):
        super().__init__(**kwargs)
        self.year = year

    def get_data(self, bbox):
        if self.year is None:
            raise Exception('NdviSentinel2.get_data() requires a year value')

        start_date = "%s-01-01" % self.year
        end_date = "%s-12-31" % self.year

        # Compute NDVI for each image
        def calculate_ndvi(image):
            ndvi = (image
                    .normalizedDifference(['B8', 'B4'])
                    .rename('NDVI'))
            return image.addBands(ndvi)

        s2 = ee.ImageCollection("COPERNICUS/S2_HARMONIZED")
        ndvi = (s2
                .filterBounds(ee.Geometry.BBox(*bbox))
                .filterDate(start_date, end_date)
                .map(calculate_ndvi)
                .select('NDVI')
                 )

        ndvi_mosaic = ndvi.qualityMosaic('NDVI')

        ic = ee.ImageCollection(ndvi_mosaic)
        ndvi_data = get_image_collection(ic, bbox, 10, "NDVI")

        xdata = ndvi_data.to_dataarray()

        return xdata

    def post_processing_adjustment(self, data, ndvi_threshold=0.4, convert_to_percentage=True, **kwargs):
        """
        Applies the standard post-processing adjustment used for rendering of NDVI including masking
        to a threshold and conversion to percentage values.
        :param ndvi_threshold: (float) minimum threshold for keeping values
        :param convert_to_percentage: (bool) controls whether NDVI values are converted to a percentage
        :return: A rioxarray-format DataArray
        """
        # Remove values less than the specified threshold
        if ndvi_threshold is not None:
            data = data.where(data >= ndvi_threshold)

        # Convert to percentage in byte data_type
        if convert_to_percentage is True:
            data = convert_ratio_to_percentage(data)

        return data
