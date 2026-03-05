import ee
import pytz
import xarray as xr
from datetime import datetime, time, timedelta

from city_metrix.constants import NETCDF_FILE_EXTENSION
from city_metrix.metrix_model import GeoExtent, Layer, get_image_collection
from city_metrix.metrix_tools import is_date

DEFAULT_SPATIAL_RESOLUTION = 11132


class Era5HottestDay(Layer):
    OUTPUT_FILE_FORMAT = NETCDF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        start_date: starting date for data retrieval
        end_date: ending date for data retrieval
        seasonal_utc_offset: UTC-offset in hours as determined for AOI and DST usage.
    """

    def __init__(self, start_date: str = None, end_date: str = None, seasonal_utc_offset: float = 0, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.seasonal_utc_offset = seasonal_utc_offset

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION, resampling_method=None,
                 force_data_refresh=False):
        # spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        spatial_resolution = self.resolution or spatial_resolution or DEFAULT_SPATIAL_RESOLUTION

        if not is_date(self.start_date) or not is_date(self.end_date):
            raise Exception(
                f"Invalid date specification: start_date:{self.start_date}, end_date:{self.end_date}.")

        # Buffer the bbox by half the spatial resolution to ensure we capture data
        # for small cities where the grid cell size may be larger than the city itself.
        buffered_utm_bbox = bbox.buffer_utm_bbox(spatial_resolution/2)
        buffered_ee_rectangle = buffered_utm_bbox.to_ee_rectangle()

        dataset_daily = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")
        dataset_land = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY")
        dataset_general = ee.ImageCollection("ECMWF/ERA5/HOURLY")

        era5_daily = (dataset_daily
                      .filterDate(self.start_date, self.end_date)
                      .select('temperature_2m_max')
                      )
        # Function to calculate the daily max temperature for the AOI

        def daily_max_temperature(image):
            daily_max = image.select('temperature_2m_max').reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=buffered_ee_rectangle['ee_geometry'],
                scale=spatial_resolution,
                bestEffort=True
            ).values().get(0)

            return image.set('daily_max_temperature', daily_max)

        era5_daily_max = era5_daily.map(daily_max_temperature).filter(
            ee.Filter.notNull(['daily_max_temperature']))

        # Sort the collection based on the highest temperature and get the first image
        highest_temperature_day = era5_daily_max.sort(
            'daily_max_temperature', False).first()
        highest_temperature_day = highest_temperature_day.get(
            'system:index').getInfo()

        # system:index in format 20230101
        # Get the date of the highest temperature day
        local_date = datetime.strptime(
            highest_temperature_day, "%Y%m%d").date()

        utc_times = []
        start_local = datetime.combine(local_date, time(0, 0))
        for i in range(0, 25):
            local_time_hour = start_local + timedelta(hours=i)
            # Convert local hour back to UTC and cast as UTC time
            inverse_seasonal_utc_offset = -self.seasonal_utc_offset
            utc_time_hourly = pytz.utc.localize(
                local_time_hour + timedelta(hours=inverse_seasonal_utc_offset))
            # Rounded due to half hour offset in some cities
            # See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for the range of possible values
            # ERA5 only accepts whole hour UTC times
            # if > 30 minutes, bump up an hour
            if utc_time_hourly.minute > 30:
                utc_time_hourly = utc_time_hourly + timedelta(hours=1)
            utc_times.append(utc_time_hourly.replace(minute=0))

        utc_times_list = [dt.strftime("%Y-%m-%dT%H:%M:%S") for dt in utc_times]

        variable_land = [
            'u_component_of_wind_10m',
            'v_component_of_wind_10m',
            'dewpoint_temperature_2m',
            'temperature_2m',
            'total_precipitation',
            "surface_pressure",
        ]
        variable_general = [
            'clear_sky_direct_solar_radiation_at_surface',
            'mean_surface_direct_short_wave_radiation_flux_clear_sky',
            'mean_surface_downward_long_wave_radiation_flux_clear_sky',
            'sea_surface_temperature',
            "total_sky_direct_solar_radiation_at_surface",
            "surface_solar_radiation_downwards",
            "surface_solar_radiation_downward_clear_sky",
        ]

        era5_land = ee.ImageCollection(dataset_land
                                       .filterDate(utc_times_list[0], utc_times_list[-1])
                                       .select(variable_land)
                                       )
        data_land = get_image_collection(
            era5_land,
            buffered_ee_rectangle,
            spatial_resolution,
            "ERA5 Land Hourly",
        )

        era5_general = ee.ImageCollection(dataset_general
                                          .filterDate(utc_times_list[0], utc_times_list[-1])
                                          .select(variable_general)
                                          )
        data_general = get_image_collection(
            era5_general,
            buffered_ee_rectangle,
            spatial_resolution,
            "ERA5 Hourly",
        )

        data = xr.merge([data_land, data_general])

        # Calculate mean over y and x dimensions to get a single value for the city for each variable at each time step
        mean_ds = data.mean(dim=("y", "x"), skipna=True).load()
        # Add WGS84 lat/lon coords
        if hasattr(bbox, "latitude") and hasattr(bbox, "longitude"):
            mean_ds = mean_ds.expand_dims(
                lat=[bbox.latitude], lon=[bbox.longitude])
        else:
            mean_ds = mean_ds.expand_dims(
                lat=[bbox.centroid.y], lon=[bbox.centroid.x])

        mean_data = mean_ds.to_array()

        return mean_data
