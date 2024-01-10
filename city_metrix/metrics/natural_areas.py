from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers.natural_areas import NaturalAreas


def natural_areas(zones: GeoDataFrame) -> GeoSeries:
    return NaturalAreas().groupby(zones).mean()