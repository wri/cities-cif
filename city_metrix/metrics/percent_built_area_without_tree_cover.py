from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import TreeCanopyHeight, UrbanLandUse


def percent_built_area_without_tree_cover(
    zones: GeoDataFrame,
    height=3
) -> GeoSeries:
    """
    Get percentage of land (assuming zones are based on urban extents)
    with no tree cover (>3 Global Canopy Height dataset).
    :param zones: GeoDataFrame with geometries to collect zonal stats on
    :return: Pandas Series of percentages
    """

    tree_canopy_height = TreeCanopyHeight(height=height)

    # informal_only: urban land use class 3 for Informal
    urban_land_use = UrbanLandUse(ulu_class=3)

    built_land = urban_land_use.groupby(zones).count()
    built_land_with_tree_cover = urban_land_use.mask(tree_canopy_height).groupby(zones).count()

    return 100 * (1 - (built_land_with_tree_cover / built_land))
