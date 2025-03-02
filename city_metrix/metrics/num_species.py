from geopandas import GeoDataFrame, GeoSeries
from pandas import Series
from city_metrix.layers import SpeciesRichness, GBIFTaxonClass
from city_metrix.layers.layer_geometry import GeoExtent

def num_species(zones: GeoDataFrame, taxon: GBIFTaxonClass=GBIFTaxonClass.BIRDS, start_year=2019, end_year=2024) -> GeoSeries:
    speciesrichness_layer = SpeciesRichness(taxon, start_year, end_year)
    results = []
    for rownum in range(len(zones)):
        zone = zones.iloc[[rownum]]
        results.append(speciesrichness_layer.get_data(GeoExtent(zone.total_bounds)).species_count[rownum])
    return pd.Series(results)

def num_species_birds(zones: GeoDataFrame, start_year=2019, end_year=2024) -> GeoSeries:
    return num_species(zones, GBIFTaxonClass.BIRDS, start_year, end_year)

def num_species_arthropods(zones: GeoDataFrame, start_year=2019, end_year=2024) -> GeoSeries:
    return num_species(zones, GBIFTaxonClass.ARTHROPODS, start_year, end_year)

def num_species_vascularplants(zones: GeoDataFrame, start_year=2019, end_year=2024) -> GeoSeries:
    return num_species(zones, GBIFTaxonClass.VASCULAR_PLANTS, start_year, end_year)