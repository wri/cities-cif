from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import CamsGhg

SUPPORTED_SPECIES = CamsGhg.SUPPORTED_SPECIES
SUPPORTED_YEARS = CamsGhg.SUPPORTED_YEARS
# GWP = CamsGhg.GWP


def ghg_emissions(
    zones: GeoDataFrame, 
    species=None, 
    sector="sum", 
    co2e=True, 
    year=2023
) -> GeoSeries:
    # supported years: 2010, 2015, 2020, 2023
    if not year in SUPPORTED_YEARS:
        raise Exception(f'Unsupported year: {year}')
    
    cams_ghg = CamsGhg(species=species, sector=sector, co2e=co2e, year=year)

    cams_ghg_mean = cams_ghg.groupby(zones).mean()

    return cams_ghg_mean
