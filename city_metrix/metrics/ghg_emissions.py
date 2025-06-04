from geopandas import GeoDataFrame, GeoSeries
import pandas as pd
from pandas import DataFrame

from city_metrix.layers import CamsGhg
from city_metrix.metrics.metric import Metric

SUPPORTED_SPECIES = CamsGhg.SUPPORTED_SPECIES
SUPPORTED_YEARS = CamsGhg.SUPPORTED_YEARS


class GhgEmissions(Metric):
    def __init__(self, species=None, sector="sum", co2e=True, year=2023, **kwargs):
        super().__init__(**kwargs)
        self.species = species
        self.sector = sector
        self.co2e = co2e
        self.year = year

    def get_data(
        self, zones: GeoDataFrame, spatial_resolution: int = None
    ) -> GeoSeries:

        # supported years: 2010, 2015, 2020, 2023
        if not self.year in SUPPORTED_YEARS:
            raise Exception(f"Unsupported year: {self.year}")

        cams_ghg = CamsGhg(species=self.species, sector=self.sector, co2e=self.co2e, year=self.year)

        cams_ghg_mean = cams_ghg.groupby(zones).mean()

        return cams_ghg_mean


class GhgTimeSeries(Metric):
    def __init__(self, species=None, sector="sum", co2e=True, **kwargs):
        super().__init__(**kwargs)
        self.species = species
        self.sector = sector
        self.co2e = co2e

    def get_data(
        self, zones: GeoDataFrame, spatial_resolution: int = None
    ) -> DataFrame:

        results = []
        for year in SUPPORTED_YEARS:
            cams_ghg = CamsGhg(species=self.species, sector=self.sector, co2e=self.co2e, year=year)
            results.append(cams_ghg.groupby(zones).mean())
        results_df = pd.concat(results, axis=1)

        # Update column names
        # Determine the species value or default to "GHG" if self.species is None
        species_val = self.species if self.species is not None else "GHG"
        # Use the CO2e suffix if self.co2e is True, otherwise use an empty string
        suffix = "_as_CO2e" if self.co2e else ""
        # Construct the new column names
        results_df.columns = [f"{species_val}{suffix}_{year}" for year in SUPPORTED_YEARS]

        return results_df
