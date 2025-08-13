import pandas as pd
from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import SpeciesRichness, GBIFTaxonClass
from city_metrix.metrix_model import Metric, GeoZone, GeoExtent


class _NumberSpecies(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None
    def __init__(
        self, taxon=GBIFTaxonClass.BIRDS, start_year=2019, end_year=2024, **kwargs
    ):
        super().__init__(**kwargs)
        self.taxon = taxon
        self.start_year = start_year
        self.end_year = end_year

    def get_metric(
        self, zones: GeoZone, spatial_resolution: int = None
    ) -> pd.Series:

        speciesrichness_layer = SpeciesRichness(taxon=self.taxon, start_year=self.start_year, end_year=self.end_year)

        results = []
        for rownum in range(len(zones)):
            zone = zones.iloc[[rownum]]
            results.append(speciesrichness_layer.get_data(GeoExtent(zone.total_bounds)).species_count[0])

        return Series(results)


class BirdRichness__Species(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, start_year=2019, end_year=2024, **kwargs):
        super().__init__(**kwargs)
        self.start_year = start_year
        self.end_year = end_year

    def get_metric(
        self, zones: GeoZone, spatial_resolution: int = None
    ) -> pd.Series:
        number_species = _NumberSpecies(
            taxon=GBIFTaxonClass.BIRDS,
            start_year=self.start_year,
            end_year=self.end_year,
        )

        return number_species.get_data(zones)


class ArthropodRichness__Species(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, start_year=2019, end_year=2024, **kwargs):
        super().__init__(**kwargs)
        self.start_year = start_year
        self.end_year = end_year

    def get_metric(
        self, zones: GeoZone, spatial_resolution: int = None
    ) -> pd.Series:
        number_species = _NumberSpecies(
            taxon=GBIFTaxonClass.ARTHROPODS,
            start_year=self.start_year,
            end_year=self.end_year,
        )

        return number_species.get_data(zones)


class VascularPlantRichness__Species(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, start_year=2019, end_year=2024, **kwargs):
        super().__init__(**kwargs)
        self.start_year = start_year
        self.end_year = end_year

    def get_metric(
        self, zones: GeoDataFrame, spatial_resolution: int = None
    ) -> GeoSeries:
        number_species = _NumberSpecies(
            taxon=GBIFTaxonClass.VASCULAR_PLANTS,
            start_year=self.start_year,
            end_year=self.end_year,
        )

        return number_species.get_data(zones)
