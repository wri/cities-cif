import ee
from timezonefinder import TimezoneFinder
from pytz import timezone
from datetime import datetime
import pytz
import cdsapi
import xarray as xr
import pandas as pd

from .layer import Layer


class Era5HighTemperature(Layer):
    def __init__(self, start_date="2023-01-01", end_date="2024-01-01", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def get_data(self, bbox):
        dataset = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY")

        # Function to find the maximum value - highest temperature - pixel in each image
        def highest_temperature_image(image):
            max_pixel = image.select('temperature_2m').reduceRegion(
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
        highest_temperature_day = era5_highest.sort('highest_temperature', False).first()
        highest_temperature_day = highest_temperature_day.get('system:index').getInfo()

        year = highest_temperature_day[0:4]
        month = highest_temperature_day[4:6]
        day = highest_temperature_day[6:8]
        time = highest_temperature_day[-2:]

        min_lon, min_lat, max_lon, max_lat = bbox
        center_lon = (min_lon + max_lon) / 2
        center_lat = (min_lat + max_lat) / 2

        # Initialize TimezoneFinder
        tf = TimezoneFinder()
        # Find the timezone of the center point
        tz_name = tf.timezone_at(lng=center_lon, lat=center_lat)
        # Get the timezone object
        local_tz = timezone(tz_name)
        # Define the UTC time
        utc_time = datetime.strptime(
            f'{year}-{month}-{day} {time}:00:00', "%Y-%m-%d %H:%M:%S")

        # Convert UTC time to local time
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
        local_date = local_time.date()

        utc_times = []
        for i in range(0, 24):
            local_time_hourly = local_tz.localize(
                datetime(local_date.year, local_date.month, local_date.day, i, 0))
            utc_time_hourly = local_time_hourly.astimezone(pytz.utc)
            utc_times.append(utc_time_hourly)

        data = pd.DataFrame()
        
        c = cdsapi.Client()
        for i in range(0, 24):
            c.retrieve(
                'reanalysis-era5-single-levels',
                {
                    'product_type': 'reanalysis',
                    'variable': [
                        '10m_u_component_of_wind', '10m_v_component_of_wind', '2m_dewpoint_temperature',
                        '2m_temperature', 'clear_sky_direct_solar_radiation_at_surface', 'mean_surface_direct_short_wave_radiation_flux_clear_sky',
                        'mean_surface_downward_long_wave_radiation_flux_clear_sky', 'sea_surface_temperature', 'total_precipitation',
                    ],
                    'year': utc_times[i].year,
                    'month': utc_times[i].month,
                    'day': utc_times[i].day,
                    'time': utc_times[i].strftime("%H:00"),
                    'area': [max_lat, min_lon, min_lat, max_lon],
                    'format': 'netcdf',
                },
                f'download_{i}.nc')

            dataset = xr.open_dataset(f'download_{i}.nc')

            data.loc[i, 'utc_date'] = utc_times[i].strftime("%Y-%m-%d")
            data.loc[i, 'utc_time'] = utc_times[i].strftime("%H:00")

            variables = list(dataset.data_vars.keys())
            for variable in variables:
                data.loc[i, variable] = float(dataset[variable].mean().values)

        return data
