from geopandas import GeoDataFrame, GeoSeries
from city_metrix.layers import TreeCanopyHeight, UrbanLandUse


def percent_built_area_without_tree_cover(zones: GeoDataFrame) -> GeoSeries:
    """
    Get percentage of land (assuming zones are based on urban extents)
    with no tree cover (>3 Global Canopy Height dataset).
    :param zones: GeoDataFrame with geometries to collect zonal stats on
    :return: Pandas Series of percentages
    """
    class CanopyAbove3Meters(TreeCanopyHeight):
        def get_data(self, bbox, spatial_resolution=10):
            data = super().get_data(bbox, 10)
            return data.where(data >= 3)
    class InformalDevelopment(UrbanLandUse):
        def get_data(self, bbox, spatial_resolution=10):
            data = super().get_data(bbox, 10)
            return data.where(data == 3)

    built_up_layer = InformalDevelopment()
    tree_cover_layer = CanopyAbove3Meters()

    built_land = built_up_layer.groupby(zones).count()
    built_land_with_tree_cover = built_up_layer.mask(tree_cover_layer).groupby(zones).count()
    
    return 100 * (1 - (built_land_with_tree_cover / built_land))