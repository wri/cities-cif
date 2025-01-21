from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import TreeCanopyHeight


def percent_area_without_tree_cover(zones: GeoDataFrame) -> GeoSeries:
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

    total_area_layer = TreeCanopyHeight(spatial_resolution=10)
    tree_cover_layer = CanopyAbove5Meters(spatial_resolution=10)
    
    return 100 * (1 - (tree_cover_layer.groupby(zones).count() / total_area_layer.groupby(zones).count()))
