from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import TreeCover, EsaWorldCoverClass, EsaWorldCover


def mean_tree_cover(zones: GeoDataFrame) -> GeoSeries:
    """
    Get mean tree cover (WRI tropical tree cover).
    :param zones: GeoDataFrame with geometries to collect zonal stats on
    :return: Pandas Series of percentages
    """
    return TreeCover().groupby(zones).mean().divide(100)
