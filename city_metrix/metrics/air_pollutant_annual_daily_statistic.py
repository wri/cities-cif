from geopandas import GeoDataFrame, GeoSeries
import numpy as np
from affine import Affine

from city_metrix.layers import Cams, CamsSpecies
from city_metrix.metrics.metric import Metric
from city_metrix.layers.layer_geometry import GeoExtent

SUPPORTED_SPECIES = [CamsSpecies.CO, CamsSpecies.NO2, CamsSpecies.O3, CamsSpecies.PM10, CamsSpecies.PM25, CamsSpecies.SO2]

class CamsAnnual():
    def __init__(self, species=[], statistic='mean', year=2023):
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
                 year=2023,
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
                species = SUPPORTED_SPECIES
            return np.mean(np.mean(cams_annual, axis=1), axis=1) * [sp.value['cost_per_tonne'] for sp in species]

