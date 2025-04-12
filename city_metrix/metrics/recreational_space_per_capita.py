from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import WorldPop, OpenStreetMap, OpenStreetMapClass
from city_metrix.metrics import GeoZone
from city_metrix.metrics.metric import Metric

DEFAULT_SPATIAL_RESOLUTION = 100

class RecreationalSpacePerCapita(Metric):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 geo_zone: GeoZone,
                 spatial_resolution=DEFAULT_SPATIAL_RESOLUTION
                 ) -> GeoSeries:
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        world_pop = WorldPop()
        open_space = OpenStreetMap(osm_class=OpenStreetMapClass.OPEN_SPACE)

        # per 1000 people
        world_pop_sum = world_pop.groupby(geo_zone, spatial_resolution).sum() / 1000
        # convert square meter to hectare
        open_space_counts = open_space.mask(world_pop).groupby(geo_zone, spatial_resolution).count()
        open_space_area = open_space_counts.fillna(0) * spatial_resolution ** 2 / 10000

        return open_space_area / world_pop_sum
