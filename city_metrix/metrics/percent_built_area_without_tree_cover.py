from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import TreeCanopyHeight, EsaWorldCover, EsaWorldCoverClass


def percent_built_area_without_tree_cover(zones: GeoDataFrame) -> GeoSeries:
    """
    Get percentage of land (assuming zones are based on urban extents)
    with no tree cover (>5 Global Canopy Height dataset).
    :param zones: GeoDataFrame with geometries to collect zonal stats on
    :return: Pandas Series of percentages
    """
    class CanopyAbove5Meters(TreeCanopyHeight):
        def get_data(self, bbox):
            data = super().get_data(bbox)
            return data.where(data >= 5)

    built_up_layer = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
    tree_cover_layer = CanopyAbove5Meters(spatial_resolution=10)

    built_land = built_up_layer.groupby(zones).count()
    built_land_with_tree_cover = built_up_layer.mask(tree_cover_layer).groupby(zones).count()
    
    return 100 * (1 - (built_land_with_tree_cover / built_land))