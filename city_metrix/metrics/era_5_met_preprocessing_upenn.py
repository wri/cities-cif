from datetime import datetime
import pandas as pd
import numpy as np
from pandas import DataFrame
from pvlib import solarposition

from city_metrix.constants import CSV_FILE_EXTENSION, DEFAULT_PRODUCTION_ENV
from city_metrix.layers import Era5HottestDay
from city_metrix.metrix_model import GeoExtent, Metric, GeoZone


class Era5MetPreprocessingUPenn(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, utc_offset:float=0, **kwargs):
        super().__init__(**kwargs)
        self.utc_offset = utc_offset

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> pd.DataFrame:
        """
        Get ERA 5 data for the hottest day
        :param geo_zone: GeoZone with geometries to collect zonal stats on
        :return: Pandas Dataframe of data
        """
        bbox = GeoExtent(geo_zone.bounds, geo_zone.crs)
        era_5_data = Era5HottestDay(utc_offset=self.utc_offset).get_data_with_caching(bbox=bbox, s3_env=DEFAULT_PRODUCTION_ENV, spatial_resolution=spatial_resolution)

        t2m_var = era_5_data.sel(variable='t2m').values
        d2m_var = era_5_data.sel(variable='d2m').values
        u10_var = era_5_data.sel(variable='u10').values
        v10_var = era_5_data.sel(variable='v10').values
        sp_var = era_5_data.sel(variable='sp').values
        ssrd_var = era_5_data.sel(variable='ssrd').values
        fdir_var = era_5_data.sel(variable='fdir').values
        ssrdc_var = era_5_data.sel(variable='ssrdc').values
        cdir_var = era_5_data.sel(variable='cdir').values
        time_var = era_5_data['valid_time'].values
        lat_var = era_5_data['latitude'].values
        lon_var = era_5_data['longitude'].values

        # temps go from K to C; surface radiation goes from J/m^2 to W/m^2 (divide by 3600); wind speed from vectors (pythagorean)
        # rh calculated from temp and dew point; ghi = dni * cos(z) + dhi; z=solar zenith angle
        times = [time.astype('datetime64[s]').astype(datetime) for time in time_var]
        years = [dt.year for dt in times]
        months = [dt.month for dt in times]
        days = [dt.day for dt in times]
        hours = [dt.hour for dt in times]
        minutes = [dt.minute for dt in times]
        t2m_vals = (t2m_var[:]-273.15)
        d2m_vals = (d2m_var[:]-273.15)
        rh_vals = (100*(np.exp((17.625*d2m_vals)/(243.04+d2m_vals))/np.exp((17.625*t2m_vals)/(243.04+t2m_vals))))
        sp_vals = (sp_var[:]/100)
        wind_vals = (np.sqrt(((np.square(u10_var[:]))+(np.square(v10_var[:])))))
        ghi_vals = (ssrd_var[:]/3600)
        dni_vals = (fdir_var[:]/3600)
        clear_sky_ghi_vals = (ssrdc_var[:]/3600)
        clear_sky_dni_vals = (cdir_var[:]/3600)

        times_utc = pd.to_datetime(time_var).tz_localize('UTC')
        zenith = np.empty((len(times), len(lat_var), len(lon_var)), dtype=float)
        for i, lat in enumerate(lat_var):
            for j, lon in enumerate(lon_var):
                solpos = solarposition.get_solarposition(times_utc, lat, lon)
                zenith[:, i, j] = solpos['zenith'].values
        cos_z = np.cos(np.deg2rad(zenith))
        dhi_vals = ghi_vals - dni_vals * cos_z
        clear_sky_dhi_vals = clear_sky_ghi_vals - clear_sky_dni_vals * cos_z

        # make lat/lon grid
        latitudes = lat_var[:]
        longitudes = lon_var[:]
        latitudes_2d, longitudes_2d = np.meshgrid(latitudes, longitudes, indexing='ij')
        latitudes_flat = latitudes_2d.flatten()
        longitudes_flat = longitudes_2d.flatten()

        # create pandas dataframe
        df = pd.DataFrame({
            'lat': np.tile(latitudes_flat, len(times)),
            'lon': np.tile(longitudes_flat, len(times)),
            'Year': np.repeat(years, len(latitudes_flat)),
            'Month': np.repeat(months, len(latitudes_flat)),
            'Day': np.repeat(days, len(latitudes_flat)),
            'Hour': np.repeat(hours, len(latitudes_flat)),
            'Minute': np.repeat(minutes, len(latitudes_flat)),
            'DHI': dhi_vals.flatten(), 
            'DNI':dni_vals.flatten(),
            'GHI':ghi_vals.flatten(),
            'Clearsky DHI': clear_sky_dhi_vals.flatten(),
            'Clearsky DNI': clear_sky_dni_vals.flatten(),
            'Clearsky GHI': clear_sky_ghi_vals.flatten(),
            'Wind Speed': wind_vals.flatten(),
            'Relative Humidity': rh_vals.flatten(),
            'Temperature': t2m_vals.flatten(),
            'Pressure': sp_vals.flatten()
        })
        # round all numbers to two decimal places, which is the precision needed by the model
        df = df.round(2)

        return df
