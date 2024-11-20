from geopandas import GeoDataFrame, GeoSeries
import numpy as np

from city_metrix.layers.isochrone import Isoline
from city_metrix.layers.world_pop import WorldPop


def get_accessible_population(access_features_layer, popraster_layer, zones):
    if len(access_features_layer.gdf):
        result_series = popraster_layer.mask(access_features_layer).groupby(zones).sum()
    else:
        result_series = pd.Series([0] * len(zones))
    return result_series

def percent_population_within_isoline(zones: GeoDataFrame, cityname, amenityname, travelmode, threshold_type, threshold_value, isoline_year=2024, agesex_classes=[], worldpop_year=2020) -> GeoSeries:
    # cityname example: ARG-Buenos-Aires
	# amenityname is OSMclass names, in lowercase
	# travelmode is walk, bike, automobile, publictransit (only walk implemented for now)
	# threshold_type is distance or time
	# threshold_value is integer, in minutes or meters
	population_layer = WorldPop(agesex_classes=agesex_classes, worldpop_year=worldpop_year)
    accesszone_layer = Isoline(cityname, amenityname, travelmode, threshold_type, threshold_value, year)
    
    try:
        access_pop = get_accessible_population(accesszone_layer, population_layer, zones)
        total_pop = population_layer.groupby(zones).sum()
        result = (access_pop / total_pop) * 100
        
    except:
    # Sometimes doing entire zones gdf causes groupby to throw empty-GDF error -- workaraound is to go district-by-district
        result_gdf = GeoDataFrame({'geometry': zones['geometry']}).set_geometry('geometry').set_crs('EPSG:4326')
        access_fraction = []
        for idx in zones.index:
            access_pop = get_accessible_population(accesszone_layer, population_layer, zones.loc[[zones.index[idx]]])[0]
            total_pop = population_layer.groupby(zones.loc[[zones.index[idx]]]).sum()[0]
            if total_pop != 0:
                access_fraction.append(access_pop / total_pop)
            else:
                access_fraction.append(np.nan)

        result = access_fraction.replace([np.inf,], np.nan) * 100
        
    return result