from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import EsaWorldCover, EsaWorldCoverClass, OpenStreetMap, OpenStreetMapClass
from city_metrix.metrics.metric import Metric


class UrbanOpenSpace(Metric):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 zones: GeoDataFrame) -> GeoSeries:

        built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
        open_space = OpenStreetMap(osm_class=OpenStreetMapClass.OPEN_SPACE)

        open_space_in_built_land = open_space.mask(built_up_land).groupby(zones).count()
        built_land_counts = built_up_land.groupby(zones).count()

        return open_space_in_built_land.fillna(0) / built_land_counts
