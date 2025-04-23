from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import TreeCanopyHeight, UrbanLandUse
from city_metrix.metrics.metric import Metric

MIN_TREE_HEIGHT = 3
ULU_INFORMAL_CLASS = 3

class PercentBuiltAreaWithoutTreeCover(Metric):
    def __init__(self, height=MIN_TREE_HEIGHT, **kwargs):
        super().__init__(**kwargs)
        self.height = height

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:
        """
        Get percentage of land (assuming zones are based on urban extents)
        with no tree cover (>3 Global Canopy Height dataset).
        :param zones: GeoDataFrame with geometries to collect zonal stats on
        :return: Pandas Series of percentages
        """

        tree_canopy_height = TreeCanopyHeight(height=self.height)

        # informal_only: urban land use class 3 for Informal
        urban_land_use = UrbanLandUse(ulu_class=ULU_INFORMAL_CLASS)

        built_land = urban_land_use.groupby(zones).count()
        built_land_with_tree_cover = urban_land_use.mask(tree_canopy_height).groupby(zones).count()

        return 100 * (1 - (built_land_with_tree_cover.fillna(0) / built_land))
