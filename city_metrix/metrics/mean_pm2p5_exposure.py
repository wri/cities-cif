from geopandas import GeoDataFrame, GeoSeries
import ee
import xarray as xr
import numpy as np

from city_metrix.layers import Layer, AcagPM2p5, WorldPop, WorldPopClass, UrbanLandUse, PopWeightedPM2p5
from city_metrix.metrics.metric import Metric


class MeanPM2P5Exposure(Metric):
    def __init__(self,
                 informal_only=False,
                 **kwargs):
        super().__init__(**kwargs)
        self.informal_only = informal_only

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:

        zones = zones.reset_index()
        pm2p5_layer = AcagPM2p5()

        if self.informal_only:
            informal_layer = UrbanLandUse(ulu_class=3)
            mean_pm2p5 = pm2p5_layer.mask(informal_layer).groupby(zones).mean()
        else:
            mean_pm2p5 = pm2p5_layer.groupby(zones).mean()

        return mean_pm2p5


class MeanPM2P5ExposurePopWeighted(Metric):
    def __init__(self,
                 acag_year=2022,
                 worldpop_agesex_classes=[],
                 informal_only=False,
                 **kwargs):
        super().__init__(**kwargs)
        self.acag_year = acag_year
        self.worldpop_agesex_classes = worldpop_agesex_classes
        self.informal_only = informal_only

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:
        zones = zones.reset_index()
        pop_weighted_pm2p5 = PopWeightedPM2p5(acag_year=self.acag_year, worldpop_agesex_classes=self.worldpop_agesex_classes)

        if self.informal_only:
            informal_layer = UrbanLandUse(ulu_class=3)
            mean_pm2p5 = pop_weighted_pm2p5.mask(informal_layer).groupby(zones).mean()
        else:
            mean_pm2p5 = pop_weighted_pm2p5.groupby(zones).mean()

        return mean_pm2p5


class MeanPM2P5ExposurePopWeightedChildren(Metric):
    def __init__(self, acag_year=2022, **kwargs):
        super().__init__(**kwargs)
        self.acag_year = acag_year

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:
        pop_weighted_pm2p5_children = (MeanPM2P5ExposurePopWeighted(acag_year=self.acag_year, worldpop_agesex_classes=WorldPopClass.CHILDREN,
                                                                    informal_only=False))

        return pop_weighted_pm2p5_children.get_data(zones=zones)


class MeanPM2P5ExposurePopWeightedElderly(Metric):
    def __init__(self, acag_year=2022, **kwargs):
        super().__init__(**kwargs)
        self.acag_year = acag_year

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:
        pop_weighted_pm2p5_elderly = (MeanPM2P5ExposurePopWeighted(acag_year=self.acag_year, worldpop_agesex_classes=WorldPopClass.ELDERLY,
                                                                    informal_only=False))

        return pop_weighted_pm2p5_elderly.get_data(zones=zones)


class MeanPM2P5ExposurePopWeightedFemale(Metric):
    def __init__(self, acag_year=2022, **kwargs):
        super().__init__(**kwargs)
        self.acag_year = acag_year

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:
        pop_weighted_pm2p5_female = (MeanPM2P5ExposurePopWeighted(acag_year=self.acag_year, worldpop_agesex_classes=WorldPopClass.FEMALE,
                                                                  informal_only=False))

        return pop_weighted_pm2p5_female.get_data(zones=zones)


class MeanPM2P5ExposurePopWeightedInformal(Metric):
    def __init__(self, acag_year=2022, **kwargs):
        super().__init__(**kwargs)
        self.acag_year = acag_year

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:
        pop_weighted_pm2p5_informal = (MeanPM2P5ExposurePopWeighted(acag_year=self.acag_year, worldpop_agesex_classes=[],
                                                                  informal_only=True))
        return pop_weighted_pm2p5_informal.get_data(zones=zones)
