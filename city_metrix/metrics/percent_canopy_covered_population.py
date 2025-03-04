from geopandas import GeoDataFrame, GeoSeries
import xarray as xr
import numpy as np
import ee

from city_metrix.layers import Layer, WorldPop, WorldPopClass, UrbanLandUse, TreeCanopyCoverMask
from city_metrix.layers.layer import get_image_collection


def percent_canopy_covered_population(
    zones: GeoDataFrame,
    agesex_classes=[],
    height=3,
    percentage=30,
    informal_only=False
) -> GeoSeries:

    coverage_mask = TreeCanopyCoverMask(height=height, percentage=percentage)

    if informal_only:
        # urban land use class 3 for Informal
        urban_land_use = UrbanLandUse(ulu_class=3)
        pop_layer = WorldPop(agesex_classes=agesex_classes, masks=[urban_land_use, coverage_mask])
    
    else:
        pop_layer = WorldPop(agesex_classes=agesex_classes, masks=[coverage_mask])

    access_pop = pop_layer.groupby(zones).sum()
    total_pop = WorldPop(agesex_classes=agesex_classes).groupby(zones).sum()

    return 100 * access_pop.fillna(0) / total_pop


def percent_canopy_covered_population_elderly(zones: GeoDataFrame, height=3, percentage=30) -> GeoSeries:
    return percent_canopy_covered_population(zones, WorldPopClass.ELDERLY, height, percentage, False)


def percent_canopy_covered_population_children(zones: GeoDataFrame, height=3, percentage=30) -> GeoSeries:
    return percent_canopy_covered_population(zones, WorldPopClass.CHILDREN, height, percentage, False)


def percent_canopy_covered_population_female(zones: GeoDataFrame, height=3, percentage=30) -> GeoSeries:
    return percent_canopy_covered_population(zones, WorldPopClass.FEMALE, height, percentage, False)


def percent_canopy_covered_population_informal(zones: GeoDataFrame, height=3, percentage=30) -> GeoSeries:
    return percent_canopy_covered_population(zones, [], height, percentage, True)
