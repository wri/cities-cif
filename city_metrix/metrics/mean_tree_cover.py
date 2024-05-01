from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import TreeCover, EsaWorldCoverClass, EsaWorldCover


def mean_tree_cover(zones: GeoDataFrame, tree_cover_path: str=None) -> GeoSeries:
    """
    Get mean tree cover (WRI tropical tree cover).
    :param zones: GeoDataFrame with geometries to collect zonal stats on
    :return: Pandas Series of percentages
    """
    return TreeCover(path=tree_cover_path).groupby(zones).mean().divide(100)
