import ee
from .layer import Layer, get_image_collection

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
    def __init__(self, year=2021, spatial_resolution=10, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.spatial_resolution = spatial_resolution

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
        ndvi_data = (get_image_collection(ic, bbox, self.spatial_resolution, "NDVI")
                     .NDVI)

        return ndvi_data
