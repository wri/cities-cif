from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import WorldPop, OpenStreetMap, OpenStreetMapClass


def recreational_space_per_capita(zones: GeoDataFrame, spatial_resolution=100) -> GeoSeries:
    world_pop = WorldPop(spatial_resolution=spatial_resolution)
    open_space = OpenStreetMap(osm_class=OpenStreetMapClass.OPEN_SPACE)

    # per 1000 people
    world_pop_sum = world_pop.groupby(zones).sum() / 1000
    # convert square meter to hectare
    open_space_counts = open_space.mask(world_pop).groupby(zones).count()
    open_space_area = open_space_counts.fillna(0) * spatial_resolution ** 2 / 10000

    return open_space_area / world_pop_sum
