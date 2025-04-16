from geopandas import GeoDataFrame, GeoSeries
from pandas import Series

from city_metrix.layers import SpeciesRichness, GBIFTaxonClass
from city_metrix.layers.layer_geometry import GeoExtent
from city_metrix.metrics.metric import Metric


class NumberSpecies(Metric):
    def __init__(
        self, taxon=GBIFTaxonClass.BIRDS, start_year=2019, end_year=2024, **kwargs
    ):
        super().__init__(**kwargs)
        self.taxon = taxon
        self.start_year = start_year
        self.end_year = end_year

    def get_data(
        self, zones: GeoDataFrame, spatial_resolution: int = None
    ) -> GeoSeries:

        speciesrichness_layer = SpeciesRichness(taxon=self.taxon, start_year=self.start_year, end_year=self.end_year)

        results = []
        for rownum in range(len(zones)):
            zone = zones.iloc[[rownum]]
            results.append(speciesrichness_layer.get_data(GeoExtent(zone.total_bounds)).species_count[0])

        return Series(results)


class NumberSpeciesBirds(Metric):
    def __init__(self, start_year=2019, end_year=2024, **kwargs):
        super().__init__(**kwargs)
        self.start_year = start_year
        self.end_year = end_year

    def get_data(
        self, zones: GeoDataFrame, spatial_resolution: int = None
    ) -> GeoSeries:
        number_species = NumberSpecies(
            taxon=GBIFTaxonClass.BIRDS,
            start_year=self.start_year,
            end_year=self.end_year,
        )

        return number_species.get_data(zones)


class NumberSpeciesArthropods(Metric):
    def __init__(self, start_year=2019, end_year=2024, **kwargs):
        super().__init__(**kwargs)
        self.start_year = start_year
        self.end_year = end_year

    def get_data(
        self, zones: GeoDataFrame, spatial_resolution: int = None
    ) -> GeoSeries:
        number_species = NumberSpecies(
            taxon=GBIFTaxonClass.ARTHROPODS,
            start_year=self.start_year,
            end_year=self.end_year,
        )

        return number_species.get_data(zones)


class NumberSpeciesVascularPlants(Metric):
    def __init__(self, start_year=2019, end_year=2024, **kwargs):
        super().__init__(**kwargs)
        self.start_year = start_year
        self.end_year = end_year

    def get_data(
        self, zones: GeoDataFrame, spatial_resolution: int = None
    ) -> GeoSeries:
        number_species = NumberSpecies(
            taxon=GBIFTaxonClass.VASCULAR_PLANTS,
            start_year=self.start_year,
            end_year=self.end_year,
        )

        return number_species.get_data(zones)
