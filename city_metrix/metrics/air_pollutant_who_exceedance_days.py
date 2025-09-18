import pandas as pd
from typing import Union
import numpy as np

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import Metric, GeoExtent, GeoZone
from city_metrix.layers import Cams, CamsSpecies


def max_n_hr(arr, n):
    # Returns highest mean concentration over an n-hr period for a given array
    resampled_1hr = arr.resample({'time': '1H'}).interpolate('linear')
    max_by_offset = None
    for offs in range(n):
        resampled_n_hr = resampled_1hr.resample({'time': f'{n}H'}, offset=offs).mean().data
        candidate = resampled_n_hr.max()
        if max_by_offset is None:
            max_by_offset = candidate
        else:
            max_by_offset = max(max_by_offset, candidate)
    return max_by_offset


class AirPollutantWhoExceedance__Days(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,
                 species=None,
                 year=2023,
                 **kwargs):
        super().__init__(**kwargs)
        self.species = species
        self.year = year

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        # species is list including these elements: 'co', 'no2', 'o3', 'so2', 'pm2p5', 'pm10'
        # returns GeoSeries with column with number of days any species exceeds WHO guideline
        if self.species is not None:
            if not isinstance(self.species, (list, tuple, set)) or len(self.species) == 0 or sum([not i in CamsSpecies for i in self.species]) > 0:
                raise Exception('Argument species must be list-like containing any non-empty subset of CamsSpecies enums {0}'.format(
                    ', '.join([i.__str__().split('.')[1] for i in CamsSpecies])))
        bbox = GeoExtent(geo_zone)
        cams_layer = Cams(start_date=f'{self.year}-01-01', end_date=f'{self.year}-12-31', species=self.species)
        cams_data = cams_layer.get_data(bbox)
        if self.species is None:
            species = CamsSpecies
        else:
            species = [self.species]
        excdays = []
        for s in species:
            if s == CamsSpecies.O3:
                n = 8
                ds = np.mean(np.mean(cams_data.sel(variable=s.value['eac4_varname']), axis=1), axis=1)
                day_data = [ds[i * n: (i + 1) * n] for i in range(365)]
                maxconc_by_day = [max_n_hr(arr, n) for arr in day_data]
                excdays.append([conc > s.value['who_threshold'] for conc in maxconc_by_day])
            else:
                ds = np.mean(np.mean(cams_data.sel(variable=s.value['eac4_varname']), axis=1), axis=1)
                maxconc_by_day = ds.resample({'time': '1D'}).mean().data
                excdays.append([conc > s.value['who_threshold']
                               for conc in maxconc_by_day])
        excdays_np = np.vstack(excdays)

        return pd.Series([np.any(excdays_np, axis=0).sum()])
