import ee
import xee
import xarray as xr

from .layer import Layer, get_image_collection

""""
NDVI = Sential-2 Normalized Difference Vegetation Index
"""
class Ndvi(Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox):
        NDVIthreshold = 0.4  # decimal
        year = 2020

        yearStr = str(year)
        NDVIthresholdStr = str(NDVIthreshold)
        startdate = '' + yearStr + '-01-01'
        enddate = '' + yearStr + '-12-31'

        S2 = ee.ImageCollection("COPERNICUS/S2")
        s2.

        # dataset = ee.Image("NASA/NASADEM_HGT/001")
        # nasa_dem = ee.ImageCollection(ee.ImageCollection(dataset)
        #                               .filterBounds(ee.Geometry.BBox(*bbox))
        #                               .select('elevation')
        #                               .mean()
        #                               )
        # data = get_image_collection(nasa_dem, bbox, 30, "NASA DEM").elevation

        return data
