from geopandas import GeoDataFrame, GeoSeries
import xarray as xr
import numpy as np
from city_metrix.layers import TreeCanopyHeight, WorldPop, WorldPopClass, UrbanLandUse
from city_metrix.metrics.metric import Metric

class CanopyAreaPerResident(Metric):
    def __init__(self,  **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 zones: GeoDataFrame,
                 agesex_classes=[],
                 height=3,
                 informal_only=False) -> GeoSeries:

        world_pop = WorldPop(agesex_classes=agesex_classes)
        # tree canopy height has default spatial resolution of 1, count equals area
        tree_canopy_height = TreeCanopyHeight(height=height)

        if informal_only:
            # urban land use class 3 for Informal
            urban_land_use = UrbanLandUse(ulu_class=3)
            world_pop_sum = world_pop.mask(urban_land_use).groupby(zones).sum()
            tree_canopy_height_count = tree_canopy_height.mask(urban_land_use).groupby(zones).count()
        else:
            world_pop_sum = world_pop.groupby(zones).sum()
            tree_canopy_height_count = tree_canopy_height.groupby(zones).count()

        return tree_canopy_height_count.fillna(0) / world_pop_sum


class CanopyAreaPerResidentChildren(Metric):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 zones: GeoDataFrame,
                 height=3,) -> GeoSeries:
        return CanopyAreaPerResident().get_data(zones,
                                                WorldPopClass.CHILDREN,
                                                height,
                                                False)


class CanopyAreaPerResidentElderly(Metric):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 zones: GeoDataFrame,
                 height=3,) -> GeoSeries:
        return CanopyAreaPerResident().get_data(zones,
                                                WorldPopClass.ELDERLY,
                                                height,
                                                False)


class CanopyAreaPerResidentFemale(Metric):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 zones: GeoDataFrame,
                 height=3,) -> GeoSeries:
        return CanopyAreaPerResident().get_data(zones,
                                                WorldPopClass.FEMALE,
                                                height,
                                                False)


class CanopyAreaPerResidentInformal(Metric):
    def __init__(self, height=3, **kwargs):
        super().__init__(**kwargs)
        self.height =height

    def get_data(self,
                 zones: GeoDataFrame) -> GeoSeries:

        return CanopyAreaPerResident().get_data(zones,
                                                [],
                                                self.height,
                                                True)
