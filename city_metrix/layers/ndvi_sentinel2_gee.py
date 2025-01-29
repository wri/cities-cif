import ee

from .layer import GeoExtent, Layer, get_image_collection

DEFAULT_SPATIAL_RESOLUTION = 10

class NdviSentinel2(Layer):
    """"
    NDVI = Sentinel-2 Normalized Difference Vegetation Index
    Attributes:
        year: The satellite imaging year.
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    return: a rioxarray-format DataArray
    Author of associated Jupyter notebook: Ted.Wong@wri.org
    Notebook: https://github.com/wri/cities-cities4forests-indicators/blob/dev-eric/scripts/extract-VegetationCover.ipynb
    Reference: https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index
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

        ee_rectangle  = bbox.to_ee_rectangle()
        ndvi = (s2
                .filterBounds(ee_rectangle['ee_geometry'])
                .filterDate(start_date, end_date)
                .map(calculate_ndvi)
                .select('NDVI')
                 )

        ndvi_mosaic = ndvi.qualityMosaic('NDVI')

        ndvi_mosaic_ic = ee.ImageCollection(ndvi_mosaic)
        ndvi_data = get_image_collection(
            ndvi_mosaic_ic,
            ee_rectangle,
            spatial_resolution,
            "NDVI"
        ).NDVI

        return ndvi_data
