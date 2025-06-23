import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import TreeCanopyHeight, WorldPop, WorldPopClass, UrbanLandUse
from city_metrix.metrix_model import GeoZone, Metric


class CanopyAreaPerResident(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,
                 agesex_classes=[],
                 height=3,
                 informal_only=False,
                 **kwargs):
        super().__init__(**kwargs)
        self.agesex_classes = agesex_classes
        self.height = height
        self.informal_only = informal_only

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:

        world_pop = WorldPop(agesex_classes=self.agesex_classes)
        # tree canopy height has default spatial resolution of 1, count equals area
        tree_canopy_height = TreeCanopyHeight(height=self.height)

        if self.informal_only:
            # urban land use class 3 for Informal
            urban_land_use = UrbanLandUse(ulu_class=3)
            world_pop_sum = world_pop.mask(urban_land_use).groupby(geo_zone).sum()
            tree_canopy_height_count = tree_canopy_height.mask(urban_land_use).groupby(geo_zone).count()
        else:
            world_pop_sum = world_pop.groupby(geo_zone).sum()
            tree_canopy_height_count = tree_canopy_height.groupby(geo_zone).count()

        if not isinstance(tree_canopy_height_count, (int, float)):
            tree_canopy_height_count = tree_canopy_height_count.fillna(0)

        if isinstance(tree_canopy_height_count, pd.DataFrame):
            result = tree_canopy_height_count.copy()
            result['value'] = tree_canopy_height_count['value'] / world_pop_sum['value']
        else:
            result = tree_canopy_height_count / world_pop_sum

        return result


class CanopyAreaPerResidentChildren(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, height=3, **kwargs):
        super().__init__(**kwargs)
        self.height = height

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:
        return (CanopyAreaPerResident(WorldPopClass.CHILDREN,
                                     self.height,
                                     False)
                .get_metric(geo_zone))


class CanopyAreaPerResidentElderly(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, height=3, **kwargs):
        super().__init__(**kwargs)
        self.height = height

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:
        return (CanopyAreaPerResident(WorldPopClass.ELDERLY,
                                     self.height,
                                     False)
                .get_metric(geo_zone))


class CanopyAreaPerResidentFemale(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, height=3, **kwargs):
        super().__init__(**kwargs)
        self.height = height

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:
        return (CanopyAreaPerResident(WorldPopClass.FEMALE,
                                     self.height,
                                     False)
                .get_metric(geo_zone))

class CanopyAreaPerResidentInformal(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, height=3, **kwargs):
        super().__init__(**kwargs)
        self.height = height

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:
        return (CanopyAreaPerResident([],
                                     self.height,
                                     True)
                .get_metric(geo_zone))
