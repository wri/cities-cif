import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import Metric, GeoZone
from city_metrix.layers import (
    WorldPop,
    WorldPopClass,
    UrbanLandUse,
    TreeCanopyCoverMask,
)


class CanopyCoveredPopulation__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["worldpop_agesex_classes", "height", "informal_only", "year"]

    def __init__(
        self, worldpop_agesex_classes=[], height=3, percentage=30, informal_only=False, year=2025, **kwargs
    ):
        super().__init__(**kwargs)
        self.worldpop_agesex_classes = worldpop_agesex_classes
        self.height = height
        self.percentage = percentage
        self.informal_only = informal_only
        self.year = year
        self.unit = 'percent'

    def get_metric(self, geo_zone: GeoZone, spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:

        coverage_mask = TreeCanopyCoverMask(height=self.height, percentage=self.percentage)

        if self.informal_only:
            # urban land use class 3 for Informal
            urban_land_use = UrbanLandUse(ulu_class=3)
            pop_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes).mask(urban_land_use).mask(coverage_mask)

        else:
            pop_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes).mask(coverage_mask)

        access_pop = pop_layer.groupby(geo_zone).sum()
        total_pop = WorldPop(agesex_classes=self.worldpop_agesex_classes).groupby(geo_zone).sum()

        if not isinstance(access_pop, (int, float)):
            access_pop = access_pop.fillna(0)

        if isinstance(access_pop, pd.DataFrame):
            result = access_pop.copy()
            result['value'] = 100 * (access_pop['value'] / total_pop['value'])
        else:
            result = 100 * access_pop / total_pop

        return result


class CanopyCoveredPopulationChildren__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["height", "percentage", "year"]

    def __init__(self, height=3, percentage=30, year=2025, **kwargs):
        super().__init__(**kwargs)
        self.height = height
        self.percentage = percentage
        self.year = year
        self.unit = 'percent'

    def get_metric(self, geo_zone: GeoZone, spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        percent_canopy_covered_children = CanopyCoveredPopulation__Percent(
            worldpop_agesex_classes=WorldPopClass.CHILDREN,
            height=self.height,
            percentage=self.percentage,
            informal_only=False,
        )

        return percent_canopy_covered_children.get_metric(geo_zone=geo_zone)


class CanopyCoveredPopulationElderly__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["height", "percentage", "year"]

    def __init__(self, height=3, percentage=30, year=2025, **kwargs):
        super().__init__(**kwargs)
        self.height = height
        self.percentage = percentage
        self.year = year
        self.unit = 'percent'

    def get_metric(self, geo_zone: GeoZone, spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        percent_canopy_covered_elderly = CanopyCoveredPopulation__Percent(
            worldpop_agesex_classes=WorldPopClass.ELDERLY,
            height=self.height,
            percentage=self.percentage,
            informal_only=False,
        )

        return percent_canopy_covered_elderly.get_metric(geo_zone=geo_zone)


class CanopyCoveredPopulationFemale__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["height", "percentage", "year"]

    def __init__(self, height=3, percentage=30, year=2025, **kwargs):
        super().__init__(**kwargs)
        self.height = height
        self.percentage = percentage
        self.year = year
        self.unit = 'percent'

    def get_metric(self, geo_zone: GeoZone, spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        percent_canopy_covered_female = CanopyCoveredPopulation__Percent(
            worldpop_agesex_classes=WorldPopClass.FEMALE,
            height=self.height,
            percentage=self.percentage,
            informal_only=False,
        )

        return percent_canopy_covered_female.get_metric(geo_zone=geo_zone)


class CanopyCoveredPopulationInformal__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["height", "percentage", "year"]

    def __init__(self, height=3, percentage=30, year=2025, **kwargs):
        super().__init__(**kwargs)
        self.height = height
        self.percentage = percentage
        self.year = year
        self.unit = 'percent'

    def get_metric(self, geo_zone: GeoZone, spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        percent_canopy_covered_informal = CanopyCoveredPopulation__Percent(
            worldpop_agesex_classes=[],
            height=self.height,
            percentage=self.percentage,
            informal_only=True,
        )

        return percent_canopy_covered_informal.get_metric(geo_zone=geo_zone)
