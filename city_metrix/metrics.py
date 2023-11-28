from city_metrix.layers import Albedo, EsaWorldCoverClass, EsaWorldCover, HighLandSurfaceTemperature, TreeCover, \
    OSMOpenSpace

from geopandas import GeoDataFrame


def built_land_without_tree_cover(zones: GeoDataFrame):
    """
    Get percentage of built up land (using ESA world cover)
    with no tree cover (>0 WRI tropical tree cover).
    :param zones: GeoDataFrame with geometries to collect zonal stats on
    :return: Pandas Series of percentages
    """
    built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
    tree_cover = TreeCover(min_tree_cover=0)

    built_land = built_up_land.groupby(zones).count()
    tree_cover_in_built_land = tree_cover.mask(built_up_land).groupby(zones).count()

    percent_tree_cover_in_built_up_land = 1 - (tree_cover_in_built_land.fillna(0) / built_land)
    return percent_tree_cover_in_built_up_land


def tree_cover(zones: GeoDataFrame):
    """
    Get mean tree cover (WRI tropical tree cover).
    :param zones: GeoDataFrame with geometries to collect zonal stats on
    :return: Pandas Series of percentages
    """
    return TreeCover().groupby(zones).mean()


def surface_reflectivity(
        zones: GeoDataFrame,
        start_time="2022-01-01",
        end_time="2023-01-01",
        albedo_threshold=0.2
):
    """
    Get percentage of built up land with low albedo based on Sentinel 2 imagery.
    :param zones: GeoDataFrame with geometries to collect zonal stats over
    :param start_time: start time for collecting albedo values.
    :param end_time: end time for collecting albedo values.
    :param albedo_threshold: threshold for "low" albedo.
    :return: Pandas Series of percentages
    """
    built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
    albedo = Albedo(start_time=start_time, end_time=end_time, threshold=albedo_threshold)

    built_land_counts = built_up_land.groupby(zones).count()
    built_albedo_counts = albedo.mask(built_up_land).groupby(zones).count()

    return built_albedo_counts / built_land_counts


def high_land_surface_temperature(zones):
    """
    Get percentage of built up land with low albedo based on Sentinel 2 imagery.
    :param zones: 
    :return: 
    """
    built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
    high_lst = HighLandSurfaceTemperature()

    built_land_counts = built_up_land.groupby(zones).count()
    built_high_lst_counts = high_lst.mask(built_up_land).groupby(zones).count()

    return built_high_lst_counts.fillna(0) / built_land_counts


def urban_open_space(zones):
    built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
    open_space = OSMOpenSpace()

    open_space_in_built_land = open_space.mask(built_up_land).groupby(zones).count()
    built_land_counts = built_up_land.groupby(zones).count()

    return open_space_in_built_land.fillna(0) / built_land_counts
