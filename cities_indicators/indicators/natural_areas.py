from ..layers.esa_world_cover import EsaWorldCover
from ..io import to_raster

from xrspatial import zonal_stats
import xarray as xr
import numpy as np


class NaturalAreas:

    def calculate(self, gdf):
        esa_land = EsaWorldCover().read(gdf)
        city_raster = to_raster(gdf, snap_to=esa_land)

        def classify_naturalarea(element):
            if element == 0:
                # NO DATA
                return 0
            elif element <= 30:
                # TREE_COVER, SHRUBLAND, GRASSLAND
                return 1
            elif element <= 80:
                # CROPLAND, BUILT_UP, BARE_OR_SPARSE_VEGETATION, SNOW_AND_ICE, PERMANENT_WATER_BODIES
                return 0
            else:
                # HERBACEOUS_WET_LAND, MANGROVES, MOSS_AND_LICHEN
                return 1

        vfunc = np.vectorize(classify_naturalarea)
        esa_land_reclass = xr.apply_ufunc(vfunc, esa_land)

        natural_area = zonal_stats(zones=city_raster, values=esa_land_reclass, stats_funcs=["mean"]).set_index("zone")

        if "BIO_1_percentNaturalArea" in gdf.columns:
            del gdf["BIO_1_percentNaturalArea"]

        return gdf.set_index("index").join(natural_area).rename(columns={"mean": "BIO_1_percentNaturalArea"})
