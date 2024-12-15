import ee
import geopandas as gpd
import numpy as np
from city_metrix.layers import Layer, CamsGhg

SUPPORTED_SPECIES = CamsGhg.SUPPORTED_SPECIES
SUPPORTED_YEARS = CamsGhg.SUPPORTED_YEARS
GWP = CamsGhg.GWP

def ghg_emissions(zones, years=[2023]):
    # species is one of 'co2', 'ch4', 'n2o', 'chlorinated-hydrocarbons'
    # supported years: 2010, 2015, 2020, 2023

    for year in years:
        if not year in SUPPORTED_YEARS:
            raise Exception(f'Unsupported year {year}')

    zones_copy = zones.copy(deep=True)

    centroids = [zones.iloc[[i]].centroid for i in range(len(zones))]
    geoms = [ee.Geometry.Point(c.x[i], c.y[i]) for i, c in enumerate(centroids)]
    for species in SUPPORTED_SPECIES:
        data_ic = ee.ImageCollection(f'projects/wri-datalab/cams-glob-ant/{species}')
        for year in years:
            year_results = data_ic.filter(ee.Filter.eq('year', year))
            year_total = gpd.GeoDataFrame([0] * len(zones))
            sectors = year_results.aggregate_array('sector').getInfo()
            sectors.sort()
            for sector in sectors:
                results = year_results.filter(ee.Filter.eq('sector', sector)).first().reduceRegions(geoms, ee.Reducer.mean())
                result_Tg = gpd.GeoDataFrame([i['properties']['mean'] for i in results.getInfo()['features']])
                result_tonne = result_Tg * 1000000
                zones_copy[f'{species}_{sector}_{year}_tonnes'] = result_tonne
                zones_copy[f'{species}_{sector}_{year}_tonnes-CO2e'] = (result_tonne * GWP[species])
                if sector == 'sum':
                    year_total += (result_tonne * GWP[species])
            zones_copy[f'all-species_{year}_tonnes-CO2e'] = year_total
    return zones_copy
