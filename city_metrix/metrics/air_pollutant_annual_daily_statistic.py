import pandas as pd
from typing import Union
from city_metrix.constants import CSV_FILE_EXTENSION
from geopandas import GeoDataFrame, GeoSeries
import numpy as np
import xarray as xr
import pandas as pd
from affine import Affine

from city_metrix.layers import Cams, CamsSpecies
from city_metrix.metrix_model import Metric, GeoExtent, GeoZone

SUPPORTED_SPECIES = [CamsSpecies.CO, CamsSpecies.NO2, CamsSpecies.O3, CamsSpecies.PM10, CamsSpecies.PM25, CamsSpecies.SO2]

class _CamsAnnual__Tonnes():

    def __init__(self, species, statistic, year):
        self.statistic = statistic
        self.species = species
        self.year = year

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> xr.DataArray:
        bbox = GeoExtent(geo_zone).as_geographic_bbox()
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
        return cams_annual

class AirPollutantAnnualDailyMean__Tonnes(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["species", "year"]

    def __init__(self,
                 species=[],
                 year=2024,
                  **kwargs):
        super().__init__(**kwargs)
        self.species = species
        self.year = year
        self.unit = 'tonnes'

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> pd.DataFrame:
        bbox = GeoExtent(geo_zone)
        cams_annual = _CamsAnnual__Tonnes(species=self.species, statistic='mean', year=self.year).get_metric(geo_zone)
        if self.species:
            requested_species = self.species
        else:
            requested_species = SUPPORTED_SPECIES
        means = np.mean(np.mean(cams_annual, axis=1), axis=1)
        result = pd.DataFrame({'species': [sp.value['name'] for sp in requested_species], 'value': [float(means.sel(variable=sp.value['eac4_varname']).data) for sp in requested_species]})
        return result

class AirPollutantAnnualDailyMax__Tonnes(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["species", "year"]

    def __init__(self,
                 species=[],
                 year=2024,
                  **kwargs):
        super().__init__(**kwargs)
        self.species = species
        self.year = year
        self.unit = 'tonnes'

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> pd.DataFrame:
        bbox = GeoExtent(geo_zone)
        cams_annual = _CamsAnnual__Tonnes(species=self.species, statistic='max', year=self.year).get_metric(geo_zone)
        if self.species:
            requested_species = self.species
        else:
            requested_species = SUPPORTED_SPECIES
        maxes = np.max(np.max(cams_annual, axis=1), axis=1)
        result = pd.DataFrame({'species': [sp.value['name'] for sp in requested_species], 'value': [float(maxes.sel(variable=sp.value['eac4_varname']).data) for sp in requested_species]})
        return result

class AirPollutantAnnualDailySocialCost__USD(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["species", "year"]

    def __init__(self,
                 species=[],
                 year=2024,
                  **kwargs):
        super().__init__(**kwargs)
        self.species = species
        self.year = year
        self.unit = 'US dollars'

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> pd.DataFrame:
        bbox = GeoExtent(geo_zone)
        cams_annual = _CamsAnnual__Tonnes(species=self.species, statistic='mean', year=self.year).get_metric(geo_zone)
        if self.species:
            requested_species = self.species
        else:
            requested_species = [sp for sp in SUPPORTED_SPECIES if not np.isnan(sp.value['cost_per_tonne'])]
        means = np.mean(np.mean(cams_annual, axis=1), axis=1)
        result = pd.DataFrame({'species': [sp.value['name'] for sp in requested_species], 'value': [round(float(means.sel(variable=sp.value['eac4_varname']).data) * sp.value['cost_per_tonne']) for sp in requested_species]})
        return result
