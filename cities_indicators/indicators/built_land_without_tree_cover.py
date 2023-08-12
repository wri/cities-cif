from cities_indicators.layers.esa_world_cover import EsaWorldCover, EsaWorldCoverClass
from cities_indicators.layers.tropical_tree_cover import TropicalTreeCover

from xrspatial import zonal_stats


class BuiltLandWithTreeCover:
    RESOLUTION = 0.0001

    def calculate(self, city):
        tree_cover = TropicalTreeCover().read(city, self.RESOLUTION)
        built_up_land = EsaWorldCover().read(city, self.RESOLUTION, EsaWorldCoverClass.BUILT_UP)

        tree_cover_in_built_up_land = tree_cover.where(tree_cover > 10).where(built_up_land)

        city_raster = city.to_raster(self.RESOLUTION)
        built_up_land_count = zonal_stats(zones=city_raster, values=built_up_land, stats_funcs=["count"]).set_index("zone")
        tree_cover_in_built_up_land_count = zonal_stats(zones=city_raster, values=tree_cover_in_built_up_land, stats_funcs=["count"]).set_index("zone")


        percent_tree_cover_in_built_up_land = tree_cover_in_built_up_land_count / built_up_land_count

        return city.unit_boundaries.set_index("index").join(percent_tree_cover_in_built_up_land).rename(columns={"count": "percent_tree_cover_in_built_up_land"})

