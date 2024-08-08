def test_esa_ndvi():
    count = (
        EsaNdvi()
        .get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1)
        .count()
    )
    assert count



import ee
import xee
import xarray as xr
from shapely.geometry import box

from .layer import Layer, get_image_collection

""""
NDVI = Sential-2 Normalized Difference Vegetation Index
"""
class EsaNdvi(Layer):
    def __init__(self, start_date="2013-01-01", end_date="2023-01-01", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

    # https://gis.stackexchange.com/questions/457822/retrieving-maximum-ndvi-for-a-year-and-associated-date-for-each-pixel-in-google
    def get_data(self, bbox):
        ndvi = self.get_ndvi(bbox)

        # NDVIthreshold = 0.4  # decimal
        # year = 2020
        #
        # yearStr = str(year)
        # NDVIthresholdStr = str(NDVIthreshold)
        # startdate = '' + yearStr + '-01-01'
        # enddate = '' + yearStr + '-12-31'
        #
        # s2 = ee.ImageCollection("COPERNICUS/S2_HARMONIZED")
        #
        # green = s2.filterDate(startdate, enddate).map(self.addNDVI)

        # dataset = ee.Image("NASA/NASADEM_HGT/001")
        # nasa_dem = ee.ImageCollection(ee.ImageCollection(dataset)
        #                               .filterBounds(ee.Geometry.BBox(*bbox))
        #                               .select('elevation')
        #                               .mean()
        #                               )
        # data = get_image_collection(nasa_dem, bbox, 30, "NASA DEM").elevation

        return 2 # data

    # def get_ndvi(self, bbox):
    #     # centroid = box(*bbox).centroid
    #
    #     NDVIthreshold = 0.4  # decimal
    #     year = 2020
    #
    #     yearStr = str(year)
    #     NDVIthresholdStr = str(NDVIthreshold)
    #     startdate = '' + yearStr + '-01-01'
    #     enddate = '' + yearStr + '-12-31'
    #
    #     dataset = ee.ImageCollection("COPERNICUS/S2_HARMONIZED")
    #
    #     # green = s2.filterDate(startdate, enddate).map(self.addNDVI)
    #
    #     # dataset = ee.ImageCollection("ECMWF/ERA5/DAILY")
    #
    #     def addNDVI(image):
    #         ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    #         return image.addBands(ndvi)
    #
    #     ndvi = (dataset
    #             .filter(ee.Filter.And(
    #         ee.Filter.date(self.start_date, self.end_date),
    #                 ee.Filter.bounds(ee.Geometry.BBox(*bbox))))
    #                       )
    #
    #     green = dataset.map(addNDVI)
    #     green = green.qualityMosaic('NDVI').select('NDVI').float();
    #     greenScale = green.projection().nominalScale()
    #     # green = green.addBands(ee.Image(year).rename('time_start'))
    #     # Map.addLayer(green,{},"NDVI")
    #     greenmask = green.updateMask(green.select('NDVI').gte(NDVIthreshold))
    #
    #     g=2


import ee

# Initialize GEE
ee.Initialize()

# Define the bounding box (lon1, lat1, lon2, lat2)
bbox = ee.Geometry.Rectangle([lon1, lat1, lon2, lat2])

# Define the date range
start_date = 'YYYY-MM-DD'
end_date = 'YYYY-MM-DD'

# Load Sentinel-2 data
collection = ee.ImageCollection('COPERNICUS/S2').filterBounds(bbox).filterDate(start_date, end_date)

# Calculate NDVI
def calculate_ndvi(image):
    ndvi = image.normalizedDifference(['B8', 'B4'])
    return image.addBands(ndvi.rename('NDVI'))

ndvi_collection = collection.map(calculate_ndvi)

# Export the data
task = ee.batch.Export.image.toDrive(
    image=ndvi_collection.select('NDVI'),
    description='NDVI_export',
    folder='your_folder',
    fileNamePrefix='ndvi',
    region=bbox,
    scale=10  # Set the desired resolution (e.g., 10 meters)
)

task.start()


# import ee
#
# # Initialize GEE
# ee.Initialize()
#
# # Define the bounding box (lon1, lat1, lon2, lat2)
# bbox = ee.Geometry.Rectangle([lon1, lat1, lon2, lat2])
#
# # Define the date range
# start_date = 'YYYY-MM-DD'
# end_date = 'YYYY-MM-DD'
#
# # Load Sentinel-2 data
# collection = ee.ImageCollection('COPERNICUS/S2').filterBounds(bbox).filterDate(start_date, end_date)
#
# # Calculate NDVI
# def calculate_ndvi(image):
#     ndvi = image.normalizedDifference(['B8', 'B4'])
#     return image.addBands(ndvi.rename('NDVI'))
#
# ndvi_collection = collection.map(calculate_ndvi)
#
# # Export the data
# task = ee.batch.Export.image.toDrive(
#     image=ndvi_collection.select('NDVI'),
#     description='NDVI_export',
#     folder='your_folder',
#     fileNamePrefix='ndvi',
#     region=bbox,
#     scale=10  # Set the desired resolution (e.g., 10 meters)
# )
#
# task.start()




# import ee
#
# # Initialize GEE
# ee.Initialize()
#
# # Define your region of interest (ROI) as a polygon
# asset_polygon = ee.Geometry.Polygon(
#     [[[-122.5, 37.5],
#       [-122.5, 37.6],
#       [-122.4, 37.6],
#       [-122.4, 37.5]]])
#
# # Define the year for which you want to retrieve data
# year = 2023
#
# # Load Sentinel-2 Surface Reflectance (SR) data
# sentinel2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED') \
#     .filterBounds(asset_polygon) \
#     .filterDate(f'{year}-01-01', f'{year}-12-31') \
#     .select(['B4', 'B8'])  # Red (B4) and Near-Infrared (B8) bands
#
# # Compute NDVI for each image
# def calculate_ndvi(image):
#     ndvi = image.normalizedDifference(['B8', 'B4']).rename('ndvi')
#     return image.addBands(ndvi)
#
# sentinel2_with_ndvi = sentinel2.map(calculate_ndvi)
#
# # Compute the maximum NDVI and acquisition date for each pixel
# max_ndvi = sentinel2_with_ndvi.qualityMosaic('ndvi').select('ndvi')
# acquisition_date = sentinel2_with_ndvi.qualityMosaic('system:time_start').select('system:time_start')
#
# # Export the rasters as single-band images to Google Drive
# task_max_ndvi = ee.batch.Export.image.toDrive(
#     image=max_ndvi,
#     description=f'S2_max_ndvi_{year}',
#     folder='gee',
#     scale=10,
#     region=asset_polygon.geometry()
# )
#
# task_acquisition_date = ee.batch