from geopandas import GeoDataFrame, GeoSeries
import ee
import xarray as xr
import numpy as np

from city_metrix.layers import Layer, AcagPM2p5, WorldPop, WorldPopClass, UrbanLandUse, PopWeightedPM2p5
from city_metrix.layers.layer_geometry import GeoExtent
from city_metrix.metrics.metric import Metric


class MeanPM2P5Exposure(Metric):
    def __init__(self,
                 informal_only=False,
                 **kwargs):
        super().__init__(**kwargs)
        self.informal_only = informal_only

    def get_data(self,
                 zones: GeoDataFrame
                 ) -> GeoSeries:

        pm2p5_layer = AcagPM2p5()

        if self.informal_only:
            informal_layer = UrbanLandUse(ulu_class=3)
            mean_pm2p5 = pm2p5_layer.mask(informal_layer).groupby(zones).mean()
        else:
            mean_pm2p5 = pm2p5_layer.groupby(zones).mean()

        return mean_pm2p5


class MeanPM2P5ExposurePopWeighted(Metric):
    def __init__(self,
                 worldpop_agesex_classes=[],
                 informal_only=False,
                 **kwargs):
        super().__init__(**kwargs)
        self.worldpop_agesex_classes = worldpop_agesex_classes
        self.informal_only = informal_only

    def get_data(self,
                 zones: GeoDataFrame
                 ) -> GeoSeries:

        pop_weighted_pm2p5 = PopWeightedPM2p5(worldpop_agesex_classes=self.worldpop_agesex_classes)

        if self.informal_only:
            informal_layer = UrbanLandUse(ulu_class=3)
            mean_pm2p5 = pop_weighted_pm2p5.mask(informal_layer).groupby(zones).mean()
        else:
            mean_pm2p5 = pop_weighted_pm2p5.groupby(zones).mean()

        return mean_pm2p5


class MeanPM2P5ExposurePopWeightedChildren(Metric):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 zones: GeoDataFrame
                 ) -> GeoSeries:
        return MeanPM2P5ExposurePopWeighted().get_data(zones=zones,
                                                       worldpop_agesex_classes=[WorldPopClass.CHILDREN],
                                                       informal_only=False)


class MeanPM2P5ExposurePopWeightedElderly(Metric):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 zones: GeoDataFrame) -> GeoSeries:
        return MeanPM2P5ExposurePopWeighted().get_data(zones=zones,
                                                       worldpop_agesex_classes=[WorldPopClass.ELDERLY],
                                                       informal_only=False)


class MeanPM2P5ExposurePopWeightedChildrenFemale(Metric):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 zones: GeoDataFrame) -> GeoSeries:
        return MeanPM2P5ExposurePopWeighted().get_data(zones=zones,
                                                       worldpop_agesex_classes=[WorldPopClass.FEMALE],
                                                       informal_only=False)


class MeanPM2P5ExposurePopWeightedChildrenInformal(Metric):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 zones: GeoDataFrame) -> GeoSeries:
        return MeanPM2P5ExposurePopWeighted().get_data(zones=zones,
                                                       worldpop_agesex_classes=[],
                                                       informal_only=True)
