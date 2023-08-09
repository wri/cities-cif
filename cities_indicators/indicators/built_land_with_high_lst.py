from cities_indicators.layers.esa_world_cover import EsaWorldCover, EsaWorldCoverClass
from cities_indicators.layers.land_surface_temperature import LandSurfaceTemperature

import xarray as xr
from xrspatial import zonal_stats
import numpy as np

class BuiltUpHighLandSurfaceTemperature:
    RESOLUTION = 0.0001
    THRESHOLD_ADD = 3

    def calculate(self, city):
        LSTmean = LandSurfaceTemperature().read(city, self.RESOLUTION)
        built_up_land = EsaWorldCover().read(city, self.RESOLUTION, EsaWorldCoverClass.BUILT_UP)

        built_up_LSTmean = LSTmean.where(built_up_land)
        built_up_LSTmean_avg = built_up_LSTmean.mean()

        # Calculate threshold value
        # temp_thresh_value = np.round(built_up_LSTmean_avg * 100) / 100 + self.THRESHOLD_ADD
        temp_thresh_value = built_up_LSTmean_avg+self.THRESHOLD_ADD

        # # Apply threshold to create a binary mask
        high_lst_built_up_land = built_up_LSTmean.where(built_up_LSTmean >= temp_thresh_value)

        city_raster = city.to_raster(self.RESOLUTION)
        built_up_land_count = zonal_stats(zones=city_raster,
                                          values=built_up_land,
                                          stats_funcs=["count"]).set_index("zone")
        high_lst_built_up_land_count = zonal_stats(zones=city_raster,
                                                   values=high_lst_built_up_land,
                                                   stats_funcs=["count"]).set_index("zone")

        percent_high_lst_in_built_up_land = high_lst_built_up_land_count / built_up_land_count

        return city.boundaries.set_index("index").join(percent_high_lst_in_built_up_land).rename(
            columns={"count": "percent_high_lst_in_built_up_land"})


