import ee
from datetime import datetime, timedelta
import pytz
import cdsapi
import os
import xarray as xr
import glob

from city_metrix.constants import WGS_CRS, NETCDF_FILE_EXTENSION
from city_metrix.metrix_model import Layer, GeoExtent


class Era5HottestDay(Layer):
    OUTPUT_FILE_FORMAT = NETCDF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        start_date: starting date for data retrieval
        end_date: ending date for data retrieval
    """
    def __init__(self, start_date="2023-01-01", end_date="2024-01-01", seasonal_utc_offset:float=0, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.seasonal_utc_offset = seasonal_utc_offset

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None,
                 force_data_refresh=False):
        # Note: spatial_resolution and resampling_method arguments are ignored.

        geographic_bbox = bbox.as_geographic_bbox()

        geographic_centroid = geographic_bbox.centroid
        center_lon = geographic_centroid.x
        center_lat = geographic_centroid.y

        min_lon, min_lat, max_lon, max_lat = geographic_bbox.bounds

        dataset = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY")

        # Function to find the city mean temperature of each hour
        def hourly_mean_temperature(image):
            point_crs = WGS_CRS
            hourly_mean = image.select('temperature_2m').reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=ee.Geometry.Point([center_lon, center_lat], point_crs),
                scale=11132,
                bestEffort=True
            ).values().get(0)

            return image.set('hourly_mean_temperature', hourly_mean)

        ee_rectangle = geographic_bbox.to_ee_rectangle()
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

        # Define the UTC time
        utc_time = datetime.strptime(f'{year}-{month}-{day} {time}:00:00', "%Y-%m-%d %H:%M:%S")
        # apply utc offset to utc time to get local date
        local_date = (utc_time + timedelta(hours=self.seasonal_utc_offset)).date()

        utc_times = []
        for i in range(0, 24):
            local_time_hour = datetime(local_date.year, local_date.month, local_date.day, i, 0)
            # Convert local hour back to UTC and cast as UTC time
            inverse_seasonal_utc_offset = -self.seasonal_utc_offset
            utc_time_hourly = pytz.utc.localize(local_time_hour + timedelta(hours=inverse_seasonal_utc_offset))
            # Rounded due to half hour offset in some cities
            # See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for the range of possible values
            # ERA5 only accepts whole hour UTC times
            # if > 30 minutes, bump up an hour
            if utc_time_hourly.minute > 30:
                utc_time_hourly = utc_time_hourly + timedelta(hours=1)
            utc_times.append(utc_time_hourly.replace(minute=0))
        
        utc_dates = sorted(list(set([dt.date() for dt in utc_times])))

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
                        "surface_pressure",
                        "total_sky_direct_solar_radiation_at_surface",
                        "surface_solar_radiation_downwards",
                        "surface_solar_radiation_downward_clear_sky",
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
