from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import CanopyCoverageByPercentage, WorldPop


def canopy_covered_population(zones: GeoDataFrame, percentage=33, height=5) -> GeoSeries:
    pop_layer = WorldPop()
    coverage_layer = CanopyCoverageByPercentage(percentage=percentage, height=height, reduce_resolution=True)
    access_pop = pop_layer.mask(coverage_layer).groupby(zones).sum()
    total_pop = pop_layer.groupby(zones).sum()
    return access_pop / total_pop