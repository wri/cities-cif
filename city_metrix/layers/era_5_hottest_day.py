import ee
from timezonefinder import TimezoneFinder
from pytz import timezone
from datetime import datetime
import pytz
import cdsapi
import os
import xarray as xr

from .layer import Layer

class Era5HottestDay(Layer):
    def __init__(self, start_date="2023-01-01", end_date="2024-01-01", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def get_data(self, bbox):
        dataset = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY")

        # Function to find the city mean temperature of each hour
        def hourly_mean_temperature(image):
            hourly_mean = image.select('temperature_2m').reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=ee.Geometry.BBox(*bbox),
                scale=11132,
                bestEffort=True
            ).values().get(0)

            return image.set('hourly_mean_temperature', hourly_mean)

        era5 = ee.ImageCollection(dataset
                                  .filterBounds(ee.Geometry.BBox(*bbox))
                                  .filterDate(self.start_date, self.end_date)
                                  .select('temperature_2m')
                                  )

        era5_hourly_mean = era5.map(hourly_mean_temperature)

        # Sort the collection based on the highest temperature and get the first image
        highest_temperature_day = era5_hourly_mean.sort('hourly_mean_temperature', False).first()
        highest_temperature_day = highest_temperature_day.get('system:index').getInfo()

        # system:index in format 20230101T00
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
        utc_time = datetime.strptime(f'{year}-{month}-{day} {time}:00:00', "%Y-%m-%d %H:%M:%S")

        # Convert UTC time to local time
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
        local_date = local_time.date()

        utc_times = []
        for i in range(0, 24):
            local_time_hourly = local_tz.localize(datetime(local_date.year, local_date.month, local_date.day, i, 0))
            utc_time_hourly = local_time_hourly.astimezone(pytz.utc)
            utc_times.append(utc_time_hourly)

        utc_dates = list(set([dt.date() for dt in utc_times]))

        dataarray_list = []
        c = cdsapi.Client()
        for i in range(len(utc_dates)):
            c.retrieve(
                'reanalysis-era5-single-levels',
                {
                    'product_type': 'reanalysis',
                    'variable': [
                        '10m_u_component_of_wind', '10m_v_component_of_wind', '2m_dewpoint_temperature',
                        '2m_temperature', 'clear_sky_direct_solar_radiation_at_surface', 'mean_surface_direct_short_wave_radiation_flux_clear_sky',
                        'mean_surface_downward_long_wave_radiation_flux_clear_sky', 'sea_surface_temperature', 'total_precipitation',
                    ],
                    'year': utc_dates[i].year,
                    'month': utc_dates[i].month,
                    'day': utc_dates[i].day,
                    'time': ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00',
                             '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00',
                             '20:00', '21:00', '22:00', '23:00'],
                    'area': [max_lat, min_lon, min_lat, max_lon],
                    'data_format': 'netcdf',
                    'download_format': 'unarchived'
                },
                f'download_{i}.nc')
            
            with xr.open_dataset(f'download_{i}.nc') as dataarray:
                # Subset times for the day
                times = [valid_time.astype('datetime64[s]').astype(datetime).replace(tzinfo=pytz.UTC) for valid_time in dataarray['valid_time'].values]
                indices = [i for i, value in enumerate(times) if value in utc_times]
                subset_dataarray = dataarray.isel(valid_time=indices).load()

            dataarray_list.append(subset_dataarray)

            # Remove local file
            os.remove(f'download_{i}.nc')

        data = xr.concat(dataarray_list, dim='valid_time')
        # xarray.Dataset to xarray.DataArray
        data = data.to_array()

        return data
