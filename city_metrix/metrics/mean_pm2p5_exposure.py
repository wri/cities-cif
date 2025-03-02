from geopandas import GeoDataFrame, GeoSeries
import ee
import xarray as xr
import numpy as np
from city_metrix.layers import Layer, AcagPM2p5, WorldPop, WorldPopClass, UrbanLandUse
from city_metrix.layers.layer import get_image_collection
from city_metrix.layers.layer_geometry import GeoExtent


def mean_pm2p5_exposure(zones: GeoDataFrame, year=2022, informal_only=False) -> GeoSeries:
    pm2p5_layer = AcagPM2p5(year=year, return_above=0)
    if informal_only:
        informal_layer = UrbanLandUse(ulu_class=3)
        return pm2p5_layer.mask(informal_layer).groupby(zones).mean()
    else:
        return pm2p5_layer.groupby(zones).mean()

def mean_pm2p5_exposure_popweighted(zones: GeoDataFrame, worldpop_agesex_classes=[], worldpop_year=2020, acag_year=2022, informal_only=False) -> GeoSeries:
    ACAG_NOMINALSCALE = 1113.1949000205839
    class PopPM(Layer):
    # get_data() for this class returns DataArray with pm2.5 concentration multiplied by (pixelpop/meanpop)
        def __init__(self, worldpop_agesex_classes=[], worldpop_year=2020, acag_year=2022, acag_return_above=0, **kwargs):
            super().__init__(**kwargs)
            self.worldpop_agesex_classes = worldpop_agesex_classes
            self.worldpop_year = worldpop_year
            self.acag_year = acag_year
            self.acag_return_above = acag_return_above
        def get_data(self, bbox: GeoExtent, spatial_resolution, resampling_method=None):
            pop_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes, year=self.worldpop_year)
            pm_layer = AcagPM2p5(year=self.acag_year, return_above=self.acag_return_above)
            pop_data = pop_layer.get_data(bbox, spatial_resolution=ACAG_NOMINALSCALE)
            pm_data = pm_layer.get_data(bbox, spatial_resolution=ACAG_NOMINALSCALE)
            pm_data.data = np.multiply(np.array(pm_data), np.array(pop_data) / float(np.mean(pop_data)))  # Note: keeps attributes from original pm_data
            return pm_data


    poppm_layer = PopPM(worldpop_agesex_classes=worldpop_agesex_classes, worldpop_year=worldpop_year, acag_year=acag_year, acag_return_above=0)
    if informal_only:
        informal_layer = UrbanLandUse(ulu_class=3)
        return poppm_layer.mask(informal_layer).groupby(zones).mean()
    else:
        return poppm_layer.groupby(zones).mean()

def mean_pm2p5_exposure_popweighted_children(zones: GeoDataFrame, worldpop_year=2020, acag_year=2022, acag_return_above=0) -> GeoSeries:
    return mean_pm2p5_exposure_popweighted(zones=zones, worldpop_agesex_classes=WorldPopClass.CHILDREN, worldpop_year=2020, acag_year=2022, informal_only=False)

def mean_pm2p5_exposure_popweighted_elderly(zones: GeoDataFrame, worldpop_year=2020, acag_year=2022, acag_return_above=0) -> GeoSeries:
    return mean_pm2p5_exposure_popweighted(zones=zones, worldpop_agesex_classes=WorldPopClass.ELDERLY, worldpop_year=2020, acag_year=2022, informal_only=False)

def mean_pm2p5_exposure_popweighted_female(zones: GeoDataFrame, worldpop_year=2020, acag_year=2022, acag_return_above=0) -> GeoSeries:
    return mean_pm2p5_exposure_popweighted(zones=zones, worldpop_agesex_classes=WorldPopClass.FEMALE, worldpop_year=2020, acag_year=2022, informal_only=False)

def mean_pm2p5_exposure_popweighted_informal(zones: GeoDataFrame, worldpop_year=2020, acag_year=2022, acag_return_above=0) -> GeoSeries:
    return mean_pm2p5_exposure_popweighted(zones=zones, worldpop_agesex_classes=[], worldpop_year=2020, acag_year=2022, informal_only=True)