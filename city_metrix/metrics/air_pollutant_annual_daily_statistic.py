from geopandas import GeoDataFrame, GeoSeries
import numpy as np
from affine import Affine

from city_metrix.layers import Cams
from city_metrix.metrics.metric import Metric
from city_metrix.layers.layer_geometry import GeoExtent

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
        'cost_per_tonne': np.nan,
        'eac4_varname': 'go3'
    },
    'pm25': {
        'name': 'fine particulate matter',
        'who_threshold': 15.0,
        'cost_per_tonne': np.nan,
        'eac4_varname': 'pm2p5'
    },
    'pm10': {
        'name': 'coarse particulate matter',
        'who_threshold': 45.0,
        'cost_per_tonne': np.nan,
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

class CamsAnnual():
    def __init__(self, species=[], statistic='mean', year=2024):
        self.statistic = statistic
        self.species = species
        self.year = year

    def get_data(self, bbox: GeoExtent):
        cams = Cams(start_date=f'{self.year}-01-01', end_date=f'{self.year}-12-31', species=self.species).get_data(bbox)
        cams_daily = cams.resample({'valid_time': '1D'}).mean()

        if self.statistic == 'mean':
            cams_annual = cams_daily.resample({'valid_time': '1Y'}).mean().squeeze("valid_time")
        elif self.statistic == 'max':
            cams_annual = cams_daily.resample({'valid_time': '1Y'}).max().squeeze("valid_time")
        else:
            raise Exception(f'Unsupported stat type {self.statistic}')
        
        cams_annual = cams_annual.transpose('variable', 'y', 'x')
        
        min_lon, min_lat, max_lon, max_lat = bbox.as_geographic_bbox().bounds
        transform = Affine.translation(min_lon, max_lat) * Affine.scale(0.25, -0.25)
        cams_annual.rio.write_transform(transform, inplace=True)
        cams_annual.rio.write_crs("EPSG:4326", inplace=True)
        cams_annual = cams_annual.rio.reproject(bbox.as_utm_bbox().crs)

        # var_names = cams_annual.coords["variable"].values
        # values = cams_annual.values[:, 0, 0]
        # var_dict = dict(zip(var_names, values))
    
        return cams_annual

class AirPollutantAnnualDailyStatistic(Metric):
    def __init__(self,
                 species=[],
                 year=2024,
                 statistic='mean', # options are mean, max, cost
                  **kwargs):
        super().__init__(**kwargs)
        self.species = species
        self.statistic = statistic
        self.year = year

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:
        bbox = GeoExtent(zones.total_bounds)
        cams_annual = CamsAnnual(species=self.species, statistic=[self.statistic, 'mean'][int(self.statistic=='cost')], year=self.year).get_data(bbox)

        if self.statistic == 'mean':
            return np.mean(np.mean(cams_annual, axis=1), axis=1)
        elif self.statistic == 'max':
            return np.max(np.max(cams_annual, axis=1), axis=1)
        else: # statname = 'cost'
            if self.species:
                species = self.species
            else:
                species = list(SPECIES_INFO.keys())
            return np.mean(np.mean(cams_annual, axis=1), axis=1) * [SPECIES_INFO[sp]['cost_per_tonne'] for sp in species]

