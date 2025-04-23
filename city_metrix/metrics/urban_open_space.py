from geopandas import GeoSeries

from city_metrix.constants import GEOJSON_FILE_EXTENSION
from city_metrix.layers import EsaWorldCover, EsaWorldCoverClass, OpenStreetMap, OpenStreetMapClass
from city_metrix.metrix_model import Metric, GeoZone


class UrbanOpenSpace(Metric):
    GEOSPATIAL_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:

        built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
        open_space = OpenStreetMap(osm_class=OpenStreetMapClass.OPEN_SPACE)

        open_space_in_built_land = open_space.mask(built_up_land).groupby(geo_zone).count()
        built_land_counts = built_up_land.groupby(geo_zone).count()

        return open_space_in_built_land.fillna(0) / built_land_counts
