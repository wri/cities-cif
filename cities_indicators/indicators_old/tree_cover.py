from ..layers.tropical_tree_cover import TropicalTreeCover
from ..io import to_raster

from xrspatial import zonal_stats


class TreeCover:

    def calculate(self, gdf):
        tree_cover = TropicalTreeCover().read(gdf)
        city_raster = to_raster(gdf, snap_to=tree_cover)

        tree_cover_mean = \
            zonal_stats(zones=city_raster, values=tree_cover, stats_funcs=["mean"]).set_index("zone")
        
        percent_tree_cover = tree_cover_mean * 0.01

        if "LND_2_percentTreeCover" in gdf.columns:
            del gdf["LND_2_percentTreeCover"]

        return gdf.set_index("index").join(percent_tree_cover).rename(columns={"mean": "LND_2_percentTreeCover"})
