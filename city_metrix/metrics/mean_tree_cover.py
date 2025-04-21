from geopandas import GeoSeries

from city_metrix.constants import GEOJSON_FILE_EXTENSION
from city_metrix.layers import TreeCover
from city_metrix.metrix_model import Metric, GeoZone

class MeanTreeCover(Metric):
    GEOSPATIAL_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:
        """
        Get mean tree cover (WRI tropical tree cover).
        :param geo_zone: GeoZone with geometries to collect zonal stats on
        :return: Pandas Series of percentages
        """
        return TreeCover().groupby(geo_zone).mean().divide(100)
