from geopandas import GeoDataFrame, GeoSeries
from city_metrix.layers import OpenStreetMap, OpenStreetMapClass, WorldPop
from city_metrix.layers.layer import get_utm_zone_epsg



def percentpop_euclideanprox_openspace(zones: GeoDataFrame, distance=400) -> GeoSeries:
# (Later add agesex_classes)
    open_space = OpenStreetMap(osm_class=OpenStreetMapClass.OPEN_SPACE, buffer_distance=distance).groupby(zones)
    population = WorldPop.get_data(bbox).fillna(0)
    open_space = OpenStreetMap(osm_class=OpenStreetMapClass.OPEN_SPACE, buffer_distance=distance)
    population = WorldPop()
    population_masked_byzone = population.mask(open_space).groupby(zones)
    population_byzone = population.groupby(zones)
    result = (population_masked_byzone.mean() * population_masked_byzone.count()) / (population_byzone.mean() * population_byzone.count())
    return result
