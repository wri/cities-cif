from cities_indicators.indicators.Indicator import Indicator
from cities_indicators.layers.esa_world_cover import EsaWorldCover, EsaWorldCoverClass
from cities_indicators.layers.tropical_tree_cover import TropicalTreeCover


class BuiltLandWithoutTreeCover(Indicator):
    def calculate(self, city):
        tree_cover_in_built_up_land = TropicalTreeCover(city)
        built_up_land = EsaWorldCover(city, land_cover_class=EsaWorldCoverClass.BUILT_UP)

        #stats = get_zonal_statistics(city, tree_cover, built_up_area)

        city_raster = city.to_raster(0.0001)
        percent = stats.tree_cover_in_built_up_land / stats.tree_cover_in_built_up_land

        return percent
