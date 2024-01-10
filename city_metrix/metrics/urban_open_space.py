from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import EsaWorldCover, EsaWorldCoverClass, OSMOpenSpace


def urban_open_space(zones: GeoDataFrame) -> GeoSeries:
    built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
    open_space = OSMOpenSpace()

    open_space_in_built_land = open_space.mask(built_up_land).groupby(zones).count()
    built_land_counts = built_up_land.groupby(zones).count()

    return open_space_in_built_land.fillna(0) / built_land_counts
