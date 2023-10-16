from cities_indicators.layers.esa_world_cover import EsaWorldCover, EsaWorldCoverClass
from cities_indicators.layers.albedo import Albedo
from cities_indicators.io import to_raster

from xrspatial import zonal_stats
import numpy as np


class SurfaceReflectivity:
    LOW_ALBEDO_MAX = 0.2

    def calculate(self, gdf):
        albedo = Albedo().read(gdf)
        built_up_land = EsaWorldCover().read(gdf, snap_to=albedo, land_cover_class=EsaWorldCoverClass.BUILT_UP)
        city_raster = to_raster(gdf, snap_to=albedo)

        low_albedo_in_built_up_land = albedo.where(albedo < self.LOW_ALBEDO_MAX).where(~np.isnan(built_up_land))

        built_up_land_count = zonal_stats(zones=city_raster, values=built_up_land, stats_funcs=["count"]).set_index("zone")
        low_albedo_in_built_up_land_count = zonal_stats(zones=city_raster, values=low_albedo_in_built_up_land, stats_funcs=["count"]).set_index("zone")

        low_albedo_in_built_up_land_percent = low_albedo_in_built_up_land_count / built_up_land_count

        if "HEA_3_percentBuiltwLowAlbedo" in gdf.columns:
            del gdf["HEA_3_percentBuiltwLowAlbedo"]

        return gdf.set_index("index").join(low_albedo_in_built_up_land_percent).rename(columns={
            "count": "HEA_3_percentBuiltwLowAlbedo"
        })

