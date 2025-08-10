from typing import Union
from city_metrix.constants import CSV_FILE_EXTENSION
from geopandas import GeoDataFrame, GeoSeries
from city_metrix.metrix_model import GeoExtent, GeoZone
import pandas as pd
import shapely
from city_metrix.metrics import Metric
from city_metrix.layers.isoline import AccessibleRegion
from city_metrix.layers.world_pop import WorldPop, WorldPopClass
from city_metrix.layers.urban_land_use import UrbanLandUse

DEAULT_SPATIAL_RESOLUTION = 100
INFORMAL_CLASS = 3

class AccessPopulationPercent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, amenity, city_id, level, travel_mode, threshold, unit, worldpop_agesex_classes=[], worldpop_year=2020, informal_only=False, **kwargs):
        super().__init__(**kwargs)
        self.amenity = amenity
        self.city_id = city_id
        self.level = level
        self.travel_mode = travel_mode
        self.threshold = threshold
        self.unit = unit
        self.worldpop_agesex_classes = worldpop_agesex_classes
        self.worldpop_year = worldpop_year
        self.informal_only = informal_only

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = DEAULT_SPATIAL_RESOLUTION) -> Union[pd.DataFrame | pd.Series]:
        access_layer = AccessibleRegion(city_id=self.city_id, amenity=self.amenity, travel_mode=self.travel_mode, threshold=self.threshold, unit=self.unit)
        accesspop_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes, year=self.worldpop_year, masks=[access_layer,])
        totalpop_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes, year=self.worldpop_year)
        if self.informal_only:
            informal_layer = UrbanLandUse(ulu_class=INFORMAL_CLASS)
            accesspop_layer.masks.append(informal_layer)
            totalpop_layer.masks.append(informal_layer)
        accesspop = accesspop_layer.groupby(geo_zone).sum()
        totalpop = totalpop_layer.groupby(geo_zone).sum()

        if isinstance(natural_areas, pd.DataFrame):
            accesspop_result = accesspop.copy()
            totalpop_result = totalpop.copy()
            accesspop_result['value'] = accesspop_result['value'] / totalpop_result['value'] * 100
        else:
            accesspop_result = accesspop / totalpop * 100
        return accesspop_result

class AccessPopulationPercentAll(AccessPopulationPercent):
    def __init__(self, amenity, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=[], worldpop_year=worldpop_year, informal_only=False, **kwargs)
    def get_metric(self, geo_zone: GeoZone, spatial_resolution:int = DEAULT_SPATIAL_RESOLUTION) -> Union[pd.DataFrame | pd.Series]:
        result = AccessPopulationPercent(amenity=self.amenity, city_id=self.city_id, level=self.level, travel_mode=self.travel_mode, threshold=self.threshold, unit=self.unit, worldpop_agesex_classes=self.worldpop_agesex_classes, worldpop_year=self.worldpop_year, informal_only=self.informal_only).get_metric(geo_zone, spatial_resolution)
        return result

class AccessPopulationPercentChildren(AccessPopulationPercent):
    def __init__(self, amenity, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=WorldPopClass.CHILDREN, worldpop_year=worldpop_year, informal_only=False, **kwargs)
    def get_metric(self, geo_zone: GeoZone, spatial_resolution:int = DEAULT_SPATIAL_RESOLUTION) -> Union[pd.DataFrame | pd.Series]:
        result = AccessPopulationPercent(amenity=self.amenity, city_id=self.city_id, level=self.level, travel_mode=self.travel_mode, threshold=self.threshold, unit=self.unit, worldpop_agesex_classes=self.worldpop_agesex_classes, worldpop_year=self.worldpop_year, informal_only=self.informal_only).get_metric(geo_zone, spatial_resolution)
        return result

class AccessPopulationPercentElderly(AccessPopulationPercent):
    def __init__(self, amenity, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=WorldPopClass.ELDERLY, worldpop_year=worldpop_year, informal_only=False, **kwargs)
    def get_metric(self, geo_zone: GeoZone, spatial_resolution:int = DEAULT_SPATIAL_RESOLUTION) -> Union[pd.DataFrame | pd.Series]:
        result = AccessPopulationPercent(amenity=self.amenity, city_id=self.city_id, level=self.level, travel_mode=self.travel_mode, threshold=self.threshold, unit=self.unit, worldpop_agesex_classes=self.worldpop_agesex_classes, worldpop_year=self.worldpop_year, informal_only=self.informal_only).get_metric(geo_zone, spatial_resolution)
        return result

class AccessPopulationPercentFemale(AccessPopulationPercent):
    def __init__(self, amenity, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=WorldPopClass.FEMALE, worldpop_year=worldpop_year, informal_only=False, **kwargs)
    def get_metric(self, geo_zone: GeoZone, spatial_resolution:int = DEAULT_SPATIAL_RESOLUTION) -> Union[pd.DataFrame | pd.Series]:
        result = AccessPopulationPercent(amenity=self.amenity, city_id=self.city_id, level=self.level, travel_mode=self.travel_mode, threshold=self.threshold, unit=self.unit, worldpop_agesex_classes=self.worldpop_agesex_classes, worldpop_year=self.worldpop_year, informal_only=self.informal_only).get_metric(geo_zone, spatial_resolution)
        return result

class AccessPopulationPercentInformal(AccessPopulationPercent):
    def __init__(self, amenity, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=[], worldpop_year=worldpop_year, informal_only=True, **kwargs)
    def get_metric(self, geo_zone: GeoZone, spatial_resolution:int = DEAULT_SPATIAL_RESOLUTION) -> Union[pd.DataFrame | pd.Series]:
        result = AccessPopulationPercent(amenity=self.amenity, city_id=self.city_id, level=self.level, travel_mode=self.travel_mode, threshold=self.threshold, unit=self.unit, worldpop_agesex_classes=self.worldpop_agesex_classes, worldpop_year=self.worldpop_year, informal_only=self.informal_only).get_metric(geo_zone, spatial_resolution)
        return result