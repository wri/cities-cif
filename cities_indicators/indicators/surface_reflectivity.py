from cities_indicators.layers.esa_world_cover import EsaWorldCover, EsaWorldCoverClass
from cities_indicators.layers.albedo import Albedo

from xrspatial import zonal_stats


class SurfaceReflectivity:
    RESOLUTION = 0.0001
    LOW_ALBEDO_MAX = 0.2

    def calculate(self, city):
        albedo = Albedo().read(city, self.RESOLUTION)
        built_up_land = EsaWorldCover().read(city, self.RESOLUTION, EsaWorldCoverClass.BUILT_UP)

        low_albedo_in_built_up_land = albedo.where(albedo < self.LOW_ALBEDO_MAX).where(built_up_land)

        city_raster = city.to_raster(self.RESOLUTION)
        low_albedo_in_built_up_land_count = zonal_stats(zones=city_raster, values=low_albedo_in_built_up_land, stats_funcs=["count"]).set_index("zone")

        # TODO either get average geodesic area of pixels or reproject to equal area projection
        low_albedo_in_built_up_land_area_m2 = low_albedo_in_built_up_land_count * 10

        return city.boundaries.set_index("index").join(low_albedo_in_built_up_land_area_m2).rename(columns={"count": "low_albedo_in_built_up_land_area_m2"})

