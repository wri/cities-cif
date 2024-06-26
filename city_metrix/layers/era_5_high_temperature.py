import ee
from timezonefinder import TimezoneFinder
from pytz import timezone
from datetime import datetime
import pytz
import cdsapi
import pandas as pd
import os
from netCDF4 import num2date
import numpy as np
import netCDF4

from .layer import Layer


class Era5HighTemperature(Layer):
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

        df_list = []
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

            dataset = netCDF4.Dataset(f'download_{i}.nc')

            t2m_var = dataset.variables['t2m']
            u10_var = dataset.variables['u10']
            v10_var = dataset.variables['v10']
            sst_var = dataset.variables['sst']
            cdir_var = dataset.variables['cdir']
            sw_var = dataset.variables['msdrswrfcs']
            lw_var = dataset.variables['msdwlwrfcs']
            d2m_var = dataset.variables['d2m']
            time_var = dataset.variables['time']
            lat_var = dataset.variables['latitude']
            lon_var = dataset.variables['longitude']

            # temps go from K to C; global rad (cdir) goes from /hour to /second; wind speed from vectors (pythagorean)
            # rh calculated from temp and dew point; vpd calculated from tepm and rh
            times = num2date(time_var[:], units=time_var.units)
            t2m_vals = (t2m_var[:]-273.15)
            d2m_vals = (d2m_var[:]-273.15)
            rh_vals = (100*(np.exp((17.625*d2m_vals)/(243.04+d2m_vals))/np.exp((17.625*t2m_vals)/(243.04+t2m_vals))))
            grad_vals = (cdir_var[:]/3600)
            dir_vals = (sw_var[:])
            dif_vals = (lw_var[:])
            wtemp_vals = (sst_var[:]-273.15)
            wind_vals = (np.sqrt(((np.square(u10_var[:]))+(np.square(v10_var[:])))))
            # calc vapor pressure deficit in hPa for future utci conversion. first, get svp in pascals and then get vpd
            svp_vals = (0.61078*np.exp(t2m_vals/(t2m_vals+237.3)*17.2694))
            vpd_vals = ((svp_vals*(1-(rh_vals/100))))*10

            # make lat/lon grid
            latitudes = lat_var[:]
            longitudes = lon_var[:]
            latitudes_2d, longitudes_2d = np.meshgrid(
                latitudes, longitudes, indexing='ij')
            latitudes_flat = latitudes_2d.flatten()
            longitudes_flat = longitudes_2d.flatten()

            # create pandas dataframe
            df = pd.DataFrame({
                'time': np.repeat(times, len(latitudes_flat)),
                'lat': np.tile(latitudes_flat, len(times)),
                'lon': np.tile(longitudes_flat, len(times)),
                'temp': t2m_vals.flatten(),
                'rh': rh_vals.flatten(),
                'global_rad': grad_vals.flatten(),
                'direct_rad': dir_vals.flatten(),
                'diffuse_rad': dif_vals.flatten(),
                'water_temp': wtemp_vals.flatten(),
                'wind': wind_vals.flatten(),
                'vpd': vpd_vals.flatten()
            })
            # round all numbers to two decimal places, which is the precision needed by the model
            df = df.round(2)

            df_list.append(df)

            os.remove(f'download_{i}.nc')

        data = pd.concat(df_list, ignore_index=True)

        return data
