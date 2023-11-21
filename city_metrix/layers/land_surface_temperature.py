from .landsat_collection_2 import LandsatCollection2
from .layer import Layer

from shapely.geometry import box
import ee


class LandSurfaceTemperature(Layer):
    def __init__(self, start_date="2013-01-01", end_date="2023-01-01", hottest_90_days=False, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.hottest_90_days = hottest_90_days

    def get_data(self, bbox):
        if self.hottest_90_days:
            hottest_date = self.get_hottest_date(bbox)
            pass
        else:
            start_date = self.start_date
            end_date = self.end_date

        landsat = LandsatCollection2(
            bands=["lwir11"],
            start_date=start_date,
            end_date=end_date
        ).get_data(bbox)

        celsius_lst = (((landsat.lwir11 * 0.00341802) + 149) - 273.15)
        data = celsius_lst.mean(dim="time").compute()
        return data

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

        return hottest_date


    def write(self, output_path):
        self.data.rio.to_raster(output_path)


