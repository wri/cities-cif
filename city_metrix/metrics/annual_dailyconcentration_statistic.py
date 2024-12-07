import geopandas as gpd
import numpy as np
from city_metrix.layers import Layer, Cams

SPECIES_INFO = {
    'no2': {
        'name': 'nitrogen dioxide',
        'molar_mass': 46.0055,
        'who_threshold': 25.0,
        'eac4_varname': 'no2'
    },
    'so2': {
        'name': 'sulfur dioxide',
        'molar_mass': 64.066,
        'who_threshold': 40.0,
        'eac4_varname': 'so2'
    },
    'o3': {    # Ozone thresholds are based on 8-hour average, not 24-hour.
        'name': 'ozone',
        'molar_mass': 48.0,
        'who_threshold': 100.0,
        'eac4_varname': 'go3'
    },
    'pm25': {
        'name': 'fine particulate matter',
        'who_threshold': 15.0,
        'eac4_varname': 'pm2p5'
    },
    'pm2p5': {
        'name': 'fine particulate matter',
        'who_threshold': 15.0,
        'eac4_varname': 'pm2p5'
    },
    'pm10': {
        'name': 'coarse particulate matter',
        'who_threshold': 45.0,
        'eac4_varname': 'pm10'
    },
    'co': {
        'name': 'carbon monoxide',
        'molar_mass': 28.01,
        'who_threshold': 4000.0,
        'eac4_varname': 'co'
    }
}

def annual_dailyconcentration_statistic(zones, species, statname):
    # species is one of 'co', 'no2', 'o3', 'so2', 'pm2p5', 'pm10'
    # statname is one of 'mean', 'max'
    if not species in ['co', 'no2', 'o3', 'so2', 'pm2p5', 'pm10']:
        raise Exception(f'Unsupported pollutant species {species}')
    zones_copy = zones.copy(deep=True)
    result = []
    for rownum in range(len(zones)):
        zone = zones.iloc[[rownum]]
        cams_data = cams_layer.get_data(zone.total_bounds).sel(variable=SPECIES_INFO[species]['eac4_varname'])
        cams_data_daily = cams_data.resample({'valid_time': '1D'}).mean().data
        if statname == 'mean':
            result.append(cams_data_daily.mean())
        elif statname == 'max':
            result.append(cams_data_daily.max())
        else:
            raise Exception(f'Unsupported stat type {statname}')
    zones_copy[f'{statname}_daily_{species}'] = result
    return zones_copy