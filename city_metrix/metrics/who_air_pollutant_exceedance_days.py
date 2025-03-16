import geopandas as gpd
import numpy as np
from city_metrix.layers import Layer, Cams, CamsSpecies


def max_n_hr(arr, n):
    # Returns highest mean concentration over an n-hr period for a given array
    resampled_1hr = arr.resample({'valid_time': '1H'}).interpolate('linear')
    max_by_offset = None
    for offs in range(n):
        resampled_n_hr = resampled_1hr.resample({'valid_time': f'{n}H'}, offset=offs).mean().data
        candidate = resampled_n_hr.max()
        if max_by_offset is None:
            max_by_offset = candidate
        else:
            max_by_offset = max(max_by_offset, candidate)
    return max_by_offset

def who_air_pollutant_exceedance_days(zones, species=None):
    # species is list including these elements: 'co', 'no2', 'o3', 'so2', 'pm2p5', 'pm10'
    # returns GeoSeries with column with number of days any species exceeds WHO guideline
    if species is not None:
        if not isinstance(species, (list, tuple, set)) or len(species) == 0 or sum([not i in ['co', 'no2', 'o3', 'so2', 'pm2p5', 'pm10'] for i in species]) > 0:
            raise Exception('Argument species must be list-like containing any non-empty subset of \'co\', \'no2\', \'o3\', \'so2\', \'pm2p5\', \'pm10\'')
    zones_copy = zones.copy(deep=True)
    result = []
    for rownum in range(len(zones)):
        zone = zones.iloc[[rownum]]
        cams_data = Cams(species=species).get_data(zone.total_bounds)
        if species is None:
            species = ['co', 'no2', 'o3', 'so2', 'pm2p5', 'pm10']
        excdays = []
        for s in species:
            if s == 'o3':
                n = 8
                ds = d.sel(variable=SPECIES_INFO['o3']['eac4_varname'])
                day_data = [ds[i * n: (i + 1)* n] for i in range(365)]
                maxconc_by_day = [max_n_hr(arr, n) for arr in day_data]
                excdays.append([conc > SPECIES_INFO['o3']['who_threshold'] for conc in maxconc_by_day])
            else:
                ds = d.sel(variable=SPECIES_INFO[s]['eac4_varname'])
                maxconc_by_day = ds.resample({'valid_time': '1D'}).mean().data
                excdays.append([conc > SPECIES_INFO[s]['who_threshold'] for conc in maxconc_by_day])
        excdays_np = np.vstack(excdays)
        result.append(excdays_np.any(axis=0).sum())
    zones_copy['exceedancedays_{0}'.format('-'.join(species))] = result
    return zones_copy
