from geopandas import GeoDataFrame, GeoSeries
import xarray as xr
import numpy as np
from city_metrix.layers import TreeCanopyHeight, WorldPop, WorldPopClass, UrbanLandUse
from city_metrix.metrics.metric import Metric

class CanopyAreaPerResident(Metric):
    def __init__(self,
                 agesex_classes=[],
                 height=3,
                 informal_only=False,
                 **kwargs):
        super().__init__(**kwargs)
        self.agesex_classes = agesex_classes
        self.height = height
        self.informal_only = informal_only

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:

        world_pop = WorldPop(agesex_classes=self.agesex_classes)
        # tree canopy height has default spatial resolution of 1, count equals area
        tree_canopy_height = TreeCanopyHeight(height=self.height)

        if self.informal_only:
            # urban land use class 3 for Informal
            urban_land_use = UrbanLandUse(ulu_class=3)
            world_pop_sum = world_pop.mask(urban_land_use).groupby(zones).sum()
            tree_canopy_height_count = tree_canopy_height.mask(urban_land_use).groupby(zones).count()
        else:
            world_pop_sum = world_pop.groupby(zones).sum()
            tree_canopy_height_count = tree_canopy_height.groupby(zones).count()

        return tree_canopy_height_count.fillna(0) / world_pop_sum


class CanopyAreaPerResidentChildren(Metric):
    def __init__(self, height=3, **kwargs):
        super().__init__(**kwargs)
        self.height = height

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:
        return (CanopyAreaPerResident(WorldPopClass.CHILDREN,
                                     self.height,
                                     False)
                .get_data(zones))


class CanopyAreaPerResidentElderly(Metric):
    def __init__(self, height=3, **kwargs):
        super().__init__(**kwargs)
        self.height = height

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:
        return (CanopyAreaPerResident(WorldPopClass.ELDERLY,
                                     self.height,
                                     False)
                .get_data(zones))


class CanopyAreaPerResidentFemale(Metric):
    def __init__(self, height=3, **kwargs):
        super().__init__(**kwargs)
        self.height = height

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:
        return (CanopyAreaPerResident(WorldPopClass.FEMALE,
                                     self.height,
                                     False)
                .get_data(zones))

class CanopyAreaPerResidentInformal(Metric):
    def __init__(self, height=3, **kwargs):
        super().__init__(**kwargs)
        self.height = height

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:
        return (CanopyAreaPerResident([],
                                     self.height,
                                     True)
                .get_data(zones))
