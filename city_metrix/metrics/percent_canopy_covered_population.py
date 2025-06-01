from geopandas import GeoSeries

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import Metric, GeoZone
from city_metrix.layers import (
    WorldPop,
    WorldPopClass,
    UrbanLandUse,
    TreeCanopyCoverMask,
)


class PercentCanopyCoveredPopulation(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(
        self, worldpop_agesex_classes=[], height=3, percentage=30, informal_only=False, **kwargs
    ):
        super().__init__(**kwargs)
        self.worldpop_agesex_classes = worldpop_agesex_classes
        self.height = height
        self.percentage = percentage
        self.informal_only = informal_only

    def get_metric(
        self, geo_zone: GeoZone, spatial_resolution: int = None
    ) -> GeoSeries:

        coverage_mask = TreeCanopyCoverMask(height=self.height, percentage=self.percentage)

        if self.informal_only:
            # urban land use class 3 for Informal
            urban_land_use = UrbanLandUse(ulu_class=3)
            pop_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes, masks=[urban_land_use, coverage_mask])

        else:
            pop_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes, masks=[coverage_mask])

        access_pop = pop_layer.groupby(geo_zone).sum()
        total_pop = WorldPop(agesex_classes=self.worldpop_agesex_classes).groupby(geo_zone).sum()

        return 100 * access_pop.fillna(0) / total_pop


class PercentCanopyCoveredPopulationChildren(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, height=3, percentage=30, informal_only=False, **kwargs):
        super().__init__(**kwargs)
        self.height = height
        self.percentage = percentage
        self.informal_only = informal_only

    def get_metric(
        self, geo_zone: GeoZone, spatial_resolution: int = None
    ) -> GeoSeries:
        percent_canopy_covered_children = PercentCanopyCoveredPopulation(
            worldpop_agesex_classes=WorldPopClass.CHILDREN,
            height=self.height,
            percentage=self.percentage,
            informal_only=self.informal_only,
        )

        return percent_canopy_covered_children.get_metric(geo_zone=geo_zone)

class PercentCanopyCoveredPopulationElderly(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, height=3, percentage=30, informal_only=False, **kwargs):
        super().__init__(**kwargs)
        self.height = height
        self.percentage = percentage
        self.informal_only = informal_only

    def get_metric(
        self, geo_zone: GeoZone, spatial_resolution: int = None
    ) -> GeoSeries:
        percent_canopy_covered_elderly = PercentCanopyCoveredPopulation(
            worldpop_agesex_classes=WorldPopClass.ELDERLY,
            height=self.height,
            percentage=self.percentage,
            informal_only=self.informal_only,
        )

        return percent_canopy_covered_elderly.get_metric(geo_zone=geo_zone)

class PercentCanopyCoveredPopulationFemale(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, height=3, percentage=30, informal_only=False, **kwargs):
        super().__init__(**kwargs)
        self.height = height
        self.percentage = percentage
        self.informal_only = informal_only

    def get_metric(
        self, geo_zone: GeoZone, spatial_resolution: int = None
    ) -> GeoSeries:
        percent_canopy_covered_female = PercentCanopyCoveredPopulation(
            worldpop_agesex_classes=WorldPopClass.FEMALE,
            height=self.height,
            percentage=self.percentage,
            informal_only=self.informal_only,
        )

        return percent_canopy_covered_female.get_metric(geo_zone=geo_zone)

class PercentCanopyCoveredPopulationInformal(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, worldpop_agesex_classes=[], height=3, percentage=30, **kwargs):
        super().__init__(**kwargs)
        self.worldpop_agesex_classes = worldpop_agesex_classes
        self.height = height
        self.percentage = percentage

    def get_metric(
        self, geo_zone: GeoZone, spatial_resolution: int = None
    ) -> GeoSeries:
        percent_canopy_covered_informal = PercentCanopyCoveredPopulation(
            worldpop_agesex_classes=self.worldpop_agesex_classes,
            height=self.height,
            percentage=self.percentage,
            informal_only=True,
        )

        return percent_canopy_covered_informal.get_metric(geo_zone=geo_zone)
