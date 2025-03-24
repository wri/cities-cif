from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import NaturalAreas


def natural_areas(zones: GeoDataFrame) -> GeoSeries:
    return NaturalAreas().groupby(zones).mean()