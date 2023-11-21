from ..layers.esa_world_cover import EsaWorldCoverNaturalArea
from ..io import to_raster

from xrspatial import zonal_stats


class NaturalAreas:

    def calculate(self, gdf):
        esa_land_natural_area = EsaWorldCoverNaturalArea().read(gdf)
        city_raster = to_raster(gdf, snap_to=esa_land_natural_area)

        natural_area = zonal_stats(zones=city_raster, values=esa_land_natural_area, stats_funcs=["mean"]).set_index("zone")

        if "BIO_1_percentNaturalArea" in gdf.columns:
            del gdf["BIO_1_percentNaturalArea"]

        return gdf.set_index("index").join(natural_area).rename(columns={"mean": "BIO_1_percentNaturalArea"})
