from geopandas import GeoDataFrame, GeoSeries
import xarray as xr
import numpy as np
import ee

from city_metrix.layers import (
    Layer,
    WorldPop,
    WorldPopClass,
    UrbanLandUse,
    TreeCanopyCoverMask,
)
from city_metrix.metrics.metric import Metric


class PercentCanopyCoveredPopulation(Metric):
    def __init__(
        self, worldpop_agesex_classes=[], height=3, percentage=30, informal_only=False, **kwargs
    ):
        super().__init__(**kwargs)
        self.worldpop_agesex_classes = worldpop_agesex_classes
        self.height = height
        self.percentage = percentage
        self.informal_only = informal_only

    def get_data(
        self, zones: GeoDataFrame, spatial_resolution: int = None
    ) -> GeoSeries:

        coverage_mask = TreeCanopyCoverMask(height=self.height, percentage=self.percentage)

        if self.informal_only:
            # urban land use class 3 for Informal
            urban_land_use = UrbanLandUse(ulu_class=3)
            pop_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes, masks=[urban_land_use, coverage_mask])

        else:
            pop_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes, masks=[coverage_mask])

        access_pop = pop_layer.groupby(zones).sum()
        total_pop = WorldPop(agesex_classes=self.worldpop_agesex_classes).groupby(zones).sum()

        return 100 * access_pop.fillna(0) / total_pop


class PercentCanopyCoveredPopulationChildren(Metric):
    def __init__(self, height=3, percentage=30, informal_only=False, **kwargs):
        super().__init__(**kwargs)
        self.height = height
        self.percentage = percentage
        self.informal_only = informal_only

    def get_data(
        self, zones: GeoDataFrame, spatial_resolution: int = None
    ) -> GeoSeries:
        percent_canopy_covered_children = PercentCanopyCoveredPopulation(
            worldpop_agesex_classes=WorldPopClass.CHILDREN,
            height=self.height,
            percentage=self.percentage,
            informal_only=self.informal_only,
        )

        return percent_canopy_covered_children.get_data(zones=zones)

class PercentCanopyCoveredPopulationElderly(Metric):
    def __init__(self, height=3, percentage=30, informal_only=False, **kwargs):
        super().__init__(**kwargs)
        self.height = height
        self.percentage = percentage
        self.informal_only = informal_only

    def get_data(
        self, zones: GeoDataFrame, spatial_resolution: int = None
    ) -> GeoSeries:
        percent_canopy_covered_elderly = PercentCanopyCoveredPopulation(
            worldpop_agesex_classes=WorldPopClass.ELDERLY,
            height=self.height,
            percentage=self.percentage,
            informal_only=self.informal_only,
        )

        return percent_canopy_covered_elderly.get_data(zones=zones)

class PercentCanopyCoveredPopulationFemale(Metric):
    def __init__(self, height=3, percentage=30, informal_only=False, **kwargs):
        super().__init__(**kwargs)
        self.height = height
        self.percentage = percentage
        self.informal_only = informal_only

    def get_data(
        self, zones: GeoDataFrame, spatial_resolution: int = None
    ) -> GeoSeries:
        percent_canopy_covered_female = PercentCanopyCoveredPopulation(
            worldpop_agesex_classes=WorldPopClass.FEMALE,
            height=self.height,
            percentage=self.percentage,
            informal_only=self.informal_only,
        )

        return percent_canopy_covered_female.get_data(zones=zones)

class PercentCanopyCoveredPopulationInformal(Metric):
    def __init__(self, worldpop_agesex_classes=[], height=3, percentage=30, **kwargs):
        super().__init__(**kwargs)
        self.worldpop_agesex_classes = worldpop_agesex_classes
        self.height = height
        self.percentage = percentage

    def get_data(
        self, zones: GeoDataFrame, spatial_resolution: int = None
    ) -> GeoSeries:
        percent_canopy_covered_informal = PercentCanopyCoveredPopulation(
            worldpop_agesex_classes=self.worldpop_agesex_classes,
            height=self.height,
            percentage=self.percentage,
            informal_only=True,
        )

        return percent_canopy_covered_informal.get_data(zones=zones)
