from cities_indicators.layers.esa_world_cover import EsaWorldCover, EsaWorldCoverClass
from cities_indicators.layers.tropical_tree_cover import TropicalTreeCover
from cities_indicators.io import to_raster

from xrspatial import zonal_stats
import numpy as np


class BuiltLandWithTreeCover:
    def calculate(self, gdf):
        built_up_land = EsaWorldCover().read(gdf, land_cover_class=EsaWorldCoverClass.BUILT_UP)

        tree_cover = TropicalTreeCover().read(gdf, snap_to=built_up_land)
        city_raster = to_raster(gdf, snap_to=built_up_land)

        tree_cover_in_built_up_land = tree_cover.where(tree_cover > 0).where(~np.isnan(built_up_land))

        built_up_land_count = zonal_stats(zones=city_raster, values=built_up_land, stats_funcs=["count"]).set_index("zone")
        tree_cover_in_built_up_land_count = zonal_stats(zones=city_raster, values=tree_cover_in_built_up_land, stats_funcs=["count"]).set_index("zone")

        percent_tree_cover_in_built_up_land = 1 - (tree_cover_in_built_up_land_count / built_up_land_count)

        if "HEA_4_percentBuiltupWithoutTreeCover" in gdf.columns:
            del gdf["HEA_4_percentBuiltupWithoutTreeCover"]

        return gdf.set_index("index").join(percent_tree_cover_in_built_up_land).rename(columns={"count": "HEA_4_percentBuiltupWithoutTreeCover"})

