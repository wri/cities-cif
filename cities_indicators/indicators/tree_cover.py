from cities_indicators.layers.tropical_tree_cover import TropicalTreeCover

from xrspatial import zonal_stats


class TreeCover:

    def calculate(self, city, admin_level):
        tree_cover = TropicalTreeCover().read(city)
        city_raster = city.to_raster(admin_level, tree_cover)

        tree_cover_mean = \
            zonal_stats(zones=city_raster, values=tree_cover, stats_funcs=["mean"]).set_index("zone")
        
        percent_tree_cover = tree_cover_mean * 0.01

        return city.get_geom(admin_level).set_index("index").join(percent_tree_cover).rename(columns={"mean": "LND_2_percentTreeCover"})
