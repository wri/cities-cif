from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import EsaWorldCoverClass, TreeCover, EsaWorldCover


def built_land_with_tree_cover(zones: GeoDataFrame) -> GeoSeries:
    """
    Get percentage of built up land (using ESA world cover)
    with no tree cover (>0 WRI tropical tree cover).
    :param zones: GeoDataFrame with geometries to collect zonal stats on
    :return: Pandas Series of percentages
    """
    built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
    tree_cover = TreeCover(min_tree_cover=1)

    built_land = built_up_land.groupby(zones).count()
    tree_cover_in_built_land = tree_cover.mask(built_up_land).groupby(zones).count()

    fraction_tree_cover_in_built_up_land = (tree_cover_in_built_land.fillna(0) / built_land)
    return fraction_tree_cover_in_built_up_land
