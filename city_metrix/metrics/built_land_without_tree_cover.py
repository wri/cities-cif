from geopandas import GeoSeries

from city_metrix.constants import GEOJSON_FILE_EXTENSION
from city_metrix.layers import EsaWorldCoverClass, TreeCover, EsaWorldCover
from city_metrix.metrix_model import GeoZone, Metric


class BuiltLandWithoutTreeCover(Metric):
    GEOSPATIAL_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,  **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:
        """
        Get percentage of built up land (using ESA world cover)
        with no tree cover (>0 WRI tropical tree cover).
        :param geo_zone: GeoDataFrame with geometries to collect zonal stats on
        :return: Pandas Series of percentages
        """
        built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
        tree_cover = TreeCover(min_tree_cover=1)

        built_land = built_up_land.groupby(geo_zone).count()
        tree_cover_in_built_land = tree_cover.mask(built_up_land).groupby(geo_zone).count()

        percent_tree_cover_in_built_up_land = 1 - (tree_cover_in_built_land.fillna(0) / built_land)
        return percent_tree_cover_in_built_up_land
