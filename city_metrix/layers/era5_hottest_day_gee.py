import ee
from datetime import datetime, timedelta, time
import pytz
import xarray as xr

from city_metrix.constants import WGS_CRS, NETCDF_FILE_EXTENSION
from city_metrix.metrix_model import Layer, GeoExtent, get_image_collection
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
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        if not is_date(self.start_date) or not is_date(self.end_date):
            raise Exception(
                f"Invalid date specification: start_date:{self.start_date}, end_date:{self.end_date}.")

        geographic_bbox = bbox.as_geographic_bbox()

        geographic_centroid = geographic_bbox.centroid
        center_lon = geographic_centroid.x
        center_lat = geographic_centroid.y

        dataset_land = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY")
        dataset_general = ee.ImageCollection("ECMWF/ERA5/HOURLY")

        local_date = find_hottest_date(center_lon, center_lat, spatial_resolution, geographic_bbox, dataset_land, 
                                    self.start_date, self.end_date, self.seasonal_utc_offset)
        utc_times_list = local_date_to_utc_datetime(local_date, self.seasonal_utc_offset)        

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

        # ERA5-Land hourly data at 0.1 degree lat/lon resolution
        center_ee_rectangle = GeoExtent(bbox=(
            center_lon-0.1, center_lat-0.1, center_lon+0.1, center_lat+0.1), crs=WGS_CRS).to_ee_rectangle()

        era5_land = ee.ImageCollection(dataset_land
                                       .filterDate(utc_times_list[0], utc_times_list[-1])
                                       .select(variable_land)
                                       )
        data_land = get_image_collection(
            era5_land,
            center_ee_rectangle,
            spatial_resolution,
            "ERA5 Land Hourly",
        )

        era5_general = ee.ImageCollection(dataset_general
                                          .filterDate(utc_times_list[0], utc_times_list[-1])
                                          .select(variable_general)
                                          )
        data_general = get_image_collection(
            era5_general,
            center_ee_rectangle,
            spatial_resolution,
            "ERA5 Hourly",
        )

        data = xr.merge([data_land, data_general])

        # Find the exact (y, x, time) where temperature_2m is globally max
        flat = data['temperature_2m'].stack(points=('y', 'x', 'time'))          # shape (points,)
        imax = flat.argmax('points').item()
        y0, x0, t0 = flat['points'].to_index()[imax]      # coordinate values
        # Keep the whole time series at max temperature_2m pixel
        data = data.sel(y=y0, x=x0)

        # Add WGS84 lat/lon coords
        data = data.assign_coords(lat=[center_lat], lon=[center_lon])
        data = data.to_array()

        return data


def local_date_to_utc_datetime(local_date, seasonal_utc_offset):
    utc_times = []
    start_local = datetime.combine(local_date, time(0, 0))
    for i in range(0, 25):
        local_time_hour = start_local + timedelta(hours=i)
        # Convert local hour back to UTC and cast as UTC time
        inverse_seasonal_utc_offset = -seasonal_utc_offset
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

    return utc_times_list


def find_hottest_date(center_lon, center_lat, spatial_resolution, geographic_bbox, dataset_land, start_date, end_date, seasonal_utc_offset):
    # Function to find the city mean temperature of each hour
    def _hourly_mean_temperature(image):
        hourly_mean = image.select('temperature_2m').reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=ee.Geometry.Point([center_lon, center_lat]),
            crs=WGS_CRS,
            scale=spatial_resolution,
            bestEffort=True
        ).values().get(0)

        return image.set('hourly_mean_temperature', hourly_mean)

    ee_rectangle = geographic_bbox.to_ee_rectangle()
    era5 = ee.ImageCollection(dataset_land
                              .filterBounds(ee_rectangle['ee_geometry'])
                              .filterDate(start_date, end_date)
                              .select('temperature_2m')
                              )

    era5_hourly_mean = era5.map(_hourly_mean_temperature)

    # Sort the collection based on the highest temperature and get the first image
    highest_temperature_day = era5_hourly_mean.sort(
        'hourly_mean_temperature', False).first()
    highest_temperature_day = highest_temperature_day.get(
        'system:index').getInfo()

    # system:index in format 20230101T00
    # Define the UTC time
    utc_time = datetime.strptime(highest_temperature_day, "%Y%m%dT%H")
    # apply utc offset to utc time to get local date
    local_date = (
        utc_time + timedelta(hours=seasonal_utc_offset)).date()
    
    return local_date
