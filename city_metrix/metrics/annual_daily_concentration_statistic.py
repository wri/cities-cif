import geopandas as gpd
import numpy as np
from city_metrix.layers import Layer, Cams, CamsSpecies


def annual_daily_concentration_statistic(zones, species, statname):
    # species is one of 'co', 'no2', 'o3', 'so2', 'pm2p5', 'pm10'
    # statname is one of 'mean', 'max'
    if not species in ['co', 'no2', 'o3', 'so2', 'pm2p5', 'pm10']:
        raise Exception(f'Unsupported pollutant species {species}')
    zones_copy = zones.copy(deep=True)
    result = []
    for rownum in range(len(zones)):
        zone = zones.iloc[[rownum]]
        cams_data = Cams(species=species).get_data(zone.total_bounds)
        cams_data_daily = cams_data.resample({'valid_time': '1D'}).mean().data
        if statname == 'mean':
            result.append(cams_data_daily.mean())
        elif statname == 'max':
            result.append(cams_data_daily.max())
        else:
            raise Exception(f'Unsupported stat type {statname}')
    zones_copy[f'{statname}_daily_{species}'] = result
    return zones_copy