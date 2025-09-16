import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import Metric, GeoZone
from city_metrix.layers import CamsGhg

SUPPORTED_SPECIES = CamsGhg.SUPPORTED_SPECIES
SUPPORTED_YEARS = CamsGhg.SUPPORTED_YEARS


class GhgEmissions__Tonnes(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, species=None, sector="sum", co2e=True, year=2023, **kwargs):
        super().__init__(**kwargs)
        self.species = species
        self.sector = sector
        self.co2e = co2e
        self.year = year

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        # supported years: 2010, 2015, 2020, 2023
        if not self.year in SUPPORTED_YEARS:
            raise Exception(f"Unsupported year: {self.year}")

        cams_ghg = CamsGhg(species=self.species, sector=self.sector, co2e=self.co2e, year=self.year)

        cams_ghg_mean = cams_ghg.groupby(geo_zone).mean()

        return cams_ghg_mean
