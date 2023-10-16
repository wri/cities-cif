from cities_indicators.io import to_raster
from cities_indicators.layers.esa_world_cover import EsaWorldCover, EsaWorldCoverClass
from cities_indicators.layers.land_surface_temperature import LandSurfaceTemperature

import xarray as xr
from xrspatial import zonal_stats
import numpy as np


class BuiltUpHighLandSurfaceTemperature:
    THRESHOLD_ADD = 3

    def calculate(self, gdf):
        built_up_land = EsaWorldCover().read(gdf, land_cover_class=EsaWorldCoverClass.BUILT_UP)
        LSTmean = LandSurfaceTemperature().read(gdf, snap_to=built_up_land)
        city_raster = to_raster(gdf, snap_to=built_up_land)

        built_up_LSTmean = LSTmean.where(~np.isnan(built_up_land))
        built_up_LSTmean_avg = built_up_LSTmean.mean()

        # Calculate threshold value
        # temp_thresh_value = np.round(built_up_LSTmean_avg * 100) / 100 + self.THRESHOLD_ADD
        temp_thresh_value = built_up_LSTmean_avg + self.THRESHOLD_ADD

        # # Apply threshold to create a binary mask
        high_lst_built_up_land = built_up_LSTmean.where(built_up_LSTmean >= temp_thresh_value)

        built_up_land_count = zonal_stats(zones=city_raster,
                                          values=built_up_land,
                                          stats_funcs=["count"]).set_index("zone")
        high_lst_built_up_land_count = zonal_stats(zones=city_raster,
                                                   values=high_lst_built_up_land,
                                                   stats_funcs=["count"]).set_index("zone")

        percent_high_lst_in_built_up_land = high_lst_built_up_land_count.fillna(0) / built_up_land_count

        if "HEA_2_percentBuiltupwHighLST-2013to2022meanofmonthwhottestday" in gdf.columns:
            del gdf["HEA_2_percentBuiltupwHighLST-2013to2022meanofmonthwhottestday"]

        return gdf.set_index("index").join(percent_high_lst_in_built_up_land).rename(
            columns={"count": "HEA_2_percentBuiltupwHighLST-2013to2022meanofmonthwhottestday"})


