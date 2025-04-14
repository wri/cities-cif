import geopandas as gpd
import pandas as pd
import numpy as np
from city_metrix.layers import Layer, Cams

SPECIES_INFO = {
    'no2': {
        'name': 'nitrogen dioxide',
        'molar_mass': 46.0055,
        'who_threshold': 25.0,
        'cost_per_tonne': 67000,
        'eac4_varname': 'no2'
    },
    'so2': {
        'name': 'sulfur dioxide',
        'molar_mass': 64.066,
        'who_threshold': 40.0,
        'cost_per_tonne': 33000,
        'eac4_varname': 'so2'
    },
    'o3': {    # Ozone thresholds are based on 8-hour average, not 24-hour.
        'name': 'ozone',
        'molar_mass': 48.0,
        'who_threshold': 100.0,
        'cost_per_tonne': None,
        'eac4_varname': 'go3'
    },
    'pm25': {
        'name': 'fine particulate matter',
        'who_threshold': 15.0,
        'cost_per_tonne': None,
        'eac4_varname': 'pm2p5'
    },
    'pm10': {
        'name': 'coarse particulate matter',
        'who_threshold': 45.0
        'cost_per_tonne': None,
        'eac4_varname': 'pm10'
    },
    'co': {
        'name': 'carbon monoxide',
        'molar_mass': 28.01,
        'who_threshold': 4000.0,
        'cost_per_tonne': 250,
        'eac4_varname': 'co'
    }
}

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

class AirPollutantWhoExceedanceDays(Metric):
    def __init__(self,
                 species=None,
                  **kwargs):
        super().__init__(**kwargs)
        self.species = species

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:
    # species is list including these elements: 'co', 'no2', 'o3', 'so2', 'pm2p5', 'pm10'
    # returns GeoSeries with column with number of days any species exceeds WHO guideline
        if self.species is not None:
            if not isinstance(self.species, (list, tuple, set)) or len(self.species) == 0 or sum([not i in ['co', 'no2', 'o3', 'so2', 'pm2p5', 'pm10'] for i in self.species]) > 0:
                raise Except('Argument species must be list-like containing any non-empty subset of \'co\', \'no2\', \'o3\', \'so2\', \'pm2p5\', \'pm10\')
       result = []
        for rownum in range(len(zones)):
            zone = zones.iloc[[rownum]]
            cams_data = cams_layer.get_data(zone.total_bounds)
            if self.species is None:
                species = ['co', 'no2', 'o3', 'so2', 'pm2p5', 'pm10']
            else:
                species = self.species
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
        return pd.Series(result)
