from datetime import datetime
import pandas as pd
import numpy as np
from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import Era5HottestDay
from city_metrix.layers.layer import GeoExtent


def era_5_met_preprocessing(zones: GeoDataFrame) -> GeoSeries:
    """
    Get ERA 5 data for the hottest day
    :param zones: GeoDataFrame with geometries to collect zonal stats on
    :return: Pandas Dataframe of data
    """
    bbox = GeoExtent(zones.total_bounds, zones.crs.srs)
    era_5_data = Era5HottestDay().get_data(bbox)

    t2m_var = era_5_data.sel(variable='t2m').values
    u10_var = era_5_data.sel(variable='u10').values
    v10_var = era_5_data.sel(variable='v10').values
    sst_var = era_5_data.sel(variable='sst').values
    cdir_var = era_5_data.sel(variable='cdir').values
    sw_var = era_5_data.sel(variable='avg_sdirswrfcs').values
    lw_var = era_5_data.sel(variable='avg_sdlwrfcs').values
    d2m_var = era_5_data.sel(variable='d2m').values
    time_var = era_5_data['valid_time'].values
    lat_var = era_5_data['latitude'].values
    lon_var = era_5_data['longitude'].values

    # temps go from K to C; global rad (cdir) goes from /hour to /second; wind speed from vectors (pythagorean)
    # rh calculated from temp and dew point; vpd calculated from tepm and rh
    times = [time.astype('datetime64[s]').astype(datetime) for time in time_var]
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
    latitudes_2d, longitudes_2d = np.meshgrid(latitudes, longitudes, indexing='ij')
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

    return df
