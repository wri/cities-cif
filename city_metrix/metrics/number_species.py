import pandas as pd
from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import SpeciesRichness, GBIFTaxonClass
from city_metrix.metrix_model import Metric, GeoZone, GeoExtent


class _NumberSpecies(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(
        self, taxon=GBIFTaxonClass.BIRDS, **kwargs
    ):
        super().__init__(**kwargs)
        self.taxon = None
        self.start_year = None
        self.end_year = None

    def get_metric(
        self, zones: GeoZone, spatial_resolution: int = None
    ) -> pd.Series:

        speciesrichness_layer = SpeciesRichness(taxon=self.taxon, start_year=self.start_year, end_year=self.end_year)

        results = []
        for rownum in range(len(zones)):
            zone = zones.iloc[[rownum]]
            results.append(speciesrichness_layer.get_data(GeoExtent(zone.total_bounds)).species_count[0])

        return pd.Series(results)


class BirdRichness__Species(_NumberSpecies):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, start_year=2019, end_year=2024, **kwargs):
        super().__init__(**kwargs)
        self.taxon = GBIFTaxonClass.BIRDS
        self.start_year = start_year
        self.end_year = end_year

class ArthropodRichness__Species(_NumberSpecies):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, start_year=2019, end_year=2024, **kwargs):
        super().__init__(**kwargs)
        self.taxon = GBIFTaxonClass.ARTHROPODS
        self.start_year = start_year
        self.end_year = end_year

class VascularPlantRichness__Species(_NumberSpecies):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, start_year=2019, end_year=2024, **kwargs):
        super().__init__(**kwargs)
        self.taxon = GBIFTaxonClass.VASCULAR_PLANTS
        self.start_year = start_year
        self.end_year = end_year

