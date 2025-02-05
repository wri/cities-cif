import ee
from timezonefinder import TimezoneFinder
from pytz import timezone
from datetime import datetime
import pytz
import cdsapi
import os
import xarray as xr
import glob

from .layer import Layer
from .layer_geometry import GeoExtent


class Era5HottestDay(Layer):
    def __init__(self, start_date="2023-01-01", end_date="2024-01-01", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None):
        # Note: spatial_resolution and resampling_method arguments are ignored.

        if bbox.projection_name == 'geographic':
            min_lon = bbox.min_x
            min_lat = bbox.min_y
            max_lon = bbox.max_x
            max_lat = bbox.max_y
            centroid = bbox.centroid
        else:
            wgs_bbox = bbox.as_geographic_bbox()
            min_lon = wgs_bbox.min_x
            min_lat = wgs_bbox.min_y
            max_lon = wgs_bbox.max_x
            max_lat = wgs_bbox.max_y
            centroid = wgs_bbox.centroid
        center_lon = centroid.x
        center_lat = centroid.y

        dataset = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY")

        # Function to find the city mean temperature of each hour
        def hourly_mean_temperature(image):
            point_crs = 'EPSG:4326'
            hourly_mean = image.select('temperature_2m').reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=ee.Geometry.Point([center_lon, center_lat], point_crs),
                scale=11132,
                bestEffort=True
            ).values().get(0)

            return image.set('hourly_mean_temperature', hourly_mean)

        ee_rectangle = bbox.to_ee_rectangle()
        era5 = ee.ImageCollection(dataset
                                  .filterBounds(ee_rectangle['ee_geometry'])
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

        # {"dataType": "an"(analysis)/"fc"(forecast)/"pf"(perturbed forecast)}
        an_list = []
        fc_list = []
        c = cdsapi.Client(url='https://cds.climate.copernicus.eu/api')
        for i in range(len(utc_dates)):
            target_file = f'download_{i}.grib'
            c.retrieve(
                'reanalysis-era5-single-levels',
                {
                    'product_type': 'reanalysis',
                    'variable': [
                        '10m_u_component_of_wind',
                        '10m_v_component_of_wind',
                        '2m_dewpoint_temperature',
                        '2m_temperature',
                        'clear_sky_direct_solar_radiation_at_surface',
                        'mean_surface_direct_short_wave_radiation_flux_clear_sky',
                        'mean_surface_downward_long_wave_radiation_flux_clear_sky',
                        'sea_surface_temperature',
                        'total_precipitation',
                    ],
                    'year': utc_dates[i].year,
                    'month': utc_dates[i].month,
                    'day': utc_dates[i].day,
                    'time': [
                        '00:00', '01:00', '02:00', '03:00', '04:00', '05:00',
                        '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
                        '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
                        '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'
                    ],
                    'area': [max_lat, min_lon, min_lat, max_lon],
                    'data_format': 'grib',
                    'download_format': 'unarchived'
                },
                target_file)

            # {"dataType": "an"(analysis)/"fc"(forecast)/"pf"(perturbed forecast)}
            with xr.open_dataset(target_file, backend_kwargs={"filter_by_keys": {"dataType": "an"}}) as ds:
                # Subset times for the day
                times = [time.astype('datetime64[s]').astype(datetime).replace(tzinfo=pytz.UTC) for time in ds['time'].values]
                indices = [i for i, value in enumerate(times) if value in utc_times]
                subset_ds = ds.isel(time=indices).load()

            an_list.append(subset_ds)

            with xr.open_dataset(target_file, backend_kwargs={"filter_by_keys": {"dataType": "fc"}}) as ds:
                # reduce dimension
                ds = ds.assign_coords(datetime=ds.time + ds.step)
                ds = ds.stack(new_time=("time", "step"))
                ds = ds.swap_dims({"new_time": "datetime"}).drop_vars(["time", "step", "new_time"])
                ds = ds.rename(datetime="time")
                # Subset times for the day
                times = [time.astype('datetime64[s]').astype(datetime).replace(tzinfo=pytz.UTC) for time in ds['time'].values]
                indices = [i for i, value in enumerate(times) if value in utc_times]
                subset_ds = ds.isel(time=indices).load()

            fc_list.append(subset_ds)

            # Remove local files
            for file in glob.glob(f'download_{i}.grib*'):
                os.remove(file)

        an_data = xr.concat(an_list, dim='time')
        fc_data = xr.combine_nested(fc_list, concat_dim='time').dropna(dim='time')

        fc_data = fc_data.sel(time=~fc_data.indexes['time'].duplicated())
        fc_data = fc_data.transpose(*an_data.dims)

        data = xr.merge([an_data, fc_data], join="outer")

        # xarray.Dataset to xarray.DataArray
        data = data.to_array()

        return data
