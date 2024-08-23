from .landsat_collection_2 import LandsatCollection2
from .land_surface_temperature import LandSurfaceTemperature
from .layer import Layer

from shapely.geometry import box
import datetime
import ee


class HighLandSurfaceTemperature(Layer):
    THRESHOLD_ADD = 3

    def __init__(self, start_date="2013-01-01", end_date="2023-01-01", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def get_data(self, bbox):
        hottest_date = self.get_hottest_date(bbox)
        start_date = (hottest_date - datetime.timedelta(days=45)).strftime("%Y-%m-%d")
        end_date = (hottest_date + datetime.timedelta(days=45)).strftime("%Y-%m-%d")

        lst = LandSurfaceTemperature(start_date, end_date).get_data(bbox)
        lst_mean = lst.mean(dim=['x', 'y'])
        high_lst = lst.where(lst >= (lst_mean + self.THRESHOLD_ADD))
        return high_lst

    def get_hottest_date(self, bbox):
        centroid = box(*bbox).centroid

        dataset = ee.ImageCollection("ECMWF/ERA5/DAILY")
        AirTemperature = (dataset
                          .filter(ee.Filter.And(
            ee.Filter.date(self.start_date, self.end_date),
            ee.Filter.bounds(ee.Geometry.BBox(*bbox))))
                          .select(['maximum_2m_air_temperature'], ['tasmax'])
                          )

        # add date as a band to image collection
        def addDate(image):
            img_date = ee.Date(image.date())
            img_date = ee.Number.parse(img_date.format('YYYYMMdd'))
            return image.addBands(ee.Image(img_date).rename('date').toInt())

        withdates = AirTemperature.map(addDate)

        # create a composite with the hottest day value and dates for every location and add to map
        hottest = withdates.qualityMosaic('tasmax')

        # reduce composite to get the hottest date for centroid of ROI
        resolution = dataset.first().projection().nominalScale()
        hottest_date = str(
            ee.Number(hottest.reduceRegion(ee.Reducer.firstNonNull(), ee.Geometry.Point([centroid.x, centroid.y]), resolution).get('date')).getInfo())

        # convert to date object
        return datetime.datetime.strptime(hottest_date, "%Y%m%d").date()
