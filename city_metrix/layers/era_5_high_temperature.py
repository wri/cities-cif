import ee

from .layer import Layer, get_image_collection


class Era5HighTemperature(Layer):
    def __init__(self, start_date="2023-01-01", end_date="2024-01-01", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def get_data(self, bbox):
        dataset = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY")

        # Function to find the maximum value - highest temperature - pixel in each image
        def highest_temperature_image(image):
            max_pixel = image.reduceRegion(
                reducer=ee.Reducer.max(),
                geometry=ee.Geometry.BBox(*bbox),
                scale=11132,
                bestEffort=True
            ).values().get(0)

            return image.set('highest_temperature', max_pixel)

        era5 = ee.ImageCollection(dataset
                                  .filterBounds(ee.Geometry.BBox(*bbox))
                                  .filterDate(self.start_date, self.end_date)
                                  .select('temperature_2m')
                                  )

        era5_highest = era5.map(highest_temperature_image)

        # Sort the collection based on the highest temperature and get the first image
        highest_temperature_day = ee.ImageCollection(era5_highest.sort('highest_temperature', False).first())

        data = get_image_collection(highest_temperature_day, bbox, 11132, "ERA 5 Temperature").temperature_2m

        return data
