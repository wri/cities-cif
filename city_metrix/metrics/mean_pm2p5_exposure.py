from geopandas import GeoDataFrame, GeoSeries
import ee
import xarray as xr
import numpy as np

from city_metrix.layers import Layer, AcagPM2p5, WorldPop, WorldPopClass, UrbanLandUse, PopWeightedPM2p5


def mean_pm2p5_exposure(
        zones: GeoDataFrame,
        informal_only=False
) -> GeoSeries:

    pm2p5_layer = AcagPM2p5()

    if informal_only:
        informal_layer = UrbanLandUse(ulu_class=3)
        mean_pm2p5 = pm2p5_layer.mask(informal_layer).groupby(zones).mean()

    else:
        mean_pm2p5 = pm2p5_layer.groupby(zones).mean()

    return mean_pm2p5


def mean_pm2p5_exposure_popweighted(
        zones: GeoDataFrame,
        worldpop_agesex_classes=[],
        informal_only=False
) -> GeoSeries:

    pop_weighted_pm2p5 = PopWeightedPM2p5(worldpop_agesex_classes=worldpop_agesex_classes)
    
    if informal_only:
        informal_layer = UrbanLandUse(ulu_class=3)
        mean_pm2p5 = pop_weighted_pm2p5.mask(informal_layer).groupby(zones).mean()

    else:
        mean_pm2p5 = pop_weighted_pm2p5.groupby(zones).mean()

    return mean_pm2p5


def mean_pm2p5_exposure_popweighted_children(zones: GeoDataFrame) -> GeoSeries:
    return mean_pm2p5_exposure_popweighted(zones=zones, worldpop_agesex_classes=WorldPopClass.CHILDREN, informal_only=False)


def mean_pm2p5_exposure_popweighted_elderly(zones: GeoDataFrame) -> GeoSeries:
    return mean_pm2p5_exposure_popweighted(zones=zones, worldpop_agesex_classes=WorldPopClass.ELDERLY, informal_only=False)


def mean_pm2p5_exposure_popweighted_female(zones: GeoDataFrame) -> GeoSeries:
    return mean_pm2p5_exposure_popweighted(zones=zones, worldpop_agesex_classes=WorldPopClass.FEMALE, informal_only=False)


def mean_pm2p5_exposure_popweighted_informal(zones: GeoDataFrame) -> GeoSeries:
    return mean_pm2p5_exposure_popweighted(zones=zones, worldpop_agesex_classes=[], informal_only=True)
