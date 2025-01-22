from geopandas import GeoDataFrame, GeoSeries
from pandas import Series
import xarray as xr
import numpy as np
from city_metrix.layers import TreeCanopyHeight, WorldPop, UrbanLandUse


import xarray as xr
import numpy as np
from city_metrix.layers import TreeCanopyHeight, WorldPop, WorldPopClass, UrbanLandUse


def canopy_area_per_resident(
    zones: GeoDataFrame,
    agesex_classes=[],
    height=5,
    ulu_class=None
) -> GeoSeries:

    world_pop = WorldPop(agesex_classes=agesex_classes)
    tree_canopy_height = TreeCanopyHeight(height=height)

    if ulu_class:
        urban_land_use = UrbanLandUse(ulu_class=ulu_class)
        world_pop_sum = world_pop.mask(urban_land_use).groupby(zones).sum()
        tree_canopy_height_sum = tree_canopy_height.mask(urban_land_use).groupby(zones).sum()
    else:
        world_pop_sum = world_pop.groupby(zones).sum()
        tree_canopy_height_sum = tree_canopy_height.groupby(zones).sum()

    return tree_canopy_height_sum.fillna(0) / world_pop_sum

def canopy_area_per_resident_elderly(zones: GeoDataFrame, height=5) -> GeoSeries:
    return canopy_area_per_resident(zones, agesex_classes=['F_60', 'F_65', 'F_70', 'F_75', 'F_80', 'M_60', 'M_65', 'M_70', 'M_75', 'M_80'], height=5, informal_only=False)

def canopy_area_per_resident_children(zones: GeoDataFrame, height=5) -> GeoSeries:
    return canopy_area_per_resident(zones, agesex_classes=['F_0', 'F_1', 'F_5', 'F_10', 'M_0', 'M_1', 'M_5', 'M_10'], height=5, informal_only=False)

def canopy_area_per_resident_female(zones: GeoDataFrame, height=5) -> GeoSeries:
    return canopy_area_per_resident(zones, agesex_classes=['F_0', 'F_1', 'F_5', 'F_10', 'F_15', 'F_20', 'F_25', 'F_30', 'F_35', 'F_40', 'F_45', 'F_50', 'F_55', 'F_60', 'F_65', 'F_70', 'F_75', 'F_80'], height=5, informal_only=False)

def canopy_area_per_resident_informal(zones: GeoDataFrame, height=5) -> GeoSeries:
        return canopy_area_per_resident(zones, agesex_classes=[], height=5, informal_only=True)
