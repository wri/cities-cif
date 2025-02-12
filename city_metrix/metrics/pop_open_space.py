from geopandas import GeoDataFrame, GeoSeries
from city_metrix.layers import OpenStreetMap, OpenStreetMapClass, WorldPop


def pop_open_space(zones: GeoDataFrame, buffer_distance=400) -> GeoSeries:
# (Later add agesex_classes)
    pop = WorldPop()
    open_space = OpenStreetMap(osm_class=OpenStreetMapClass.OPEN_SPACE, buffer_distance=buffer_distance)

    pop_open_space_sum = pop.mask(open_space).groupby(zones).sum()
    pop_sum = pop.groupby(zones).sum()

    return pop_open_space_sum / pop_sum
