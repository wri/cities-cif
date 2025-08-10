from typing import Union
from city_metrix.constants import CSV_FILE_EXTENSION
from geopandas import GeoDataFrame, GeoSeries
import pandas as pd
import shapely
from city_metrix.layers import AccessibleRegion, WorldPop, WorldPopClass, UrbanLandUse
from city_metrix.metrix_model import GeoZone, Metric

DEFAULT_SPATIAL_RESOLUTION = 100
INFORMAL_CLASS = 3

class _AccessPopulationPercent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["city_id", "level", "travel_mode", "threshold", "unit"]
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
                 spatial_resolution:int = DEFAULT_SPATIAL_RESOLUTION) -> Union[pd.DataFrame | pd.Series]:
        access_layer = AccessibleRegion(amenity=self.amenity, city_id=self.city_id, level=self.level, travel_mode=self.travel_mode, threshold=self.threshold, unit=self.unit)
        accesspop_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes, year=self.worldpop_year, masks=[access_layer,])
        totalpop_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes, year=self.worldpop_year)
        if self.informal_only:
            informal_layer = UrbanLandUse(ulu_class=INFORMAL_CLASS)
            accesspop_layer.masks.append(informal_layer)
            totalpop_layer.masks.append(informal_layer)
        accesspop = accesspop_layer.groupby(geo_zone).sum()
        totalpop = totalpop_layer.groupby(geo_zone).sum()

        if isinstance(accesspop, pd.DataFrame):
            accesspop_result = accesspop.copy()
            totalpop_result = totalpop.copy()
            accesspop_result['value'] = accesspop_result['value'] / totalpop_result['value'] * 100
        else:
            accesspop_result = accesspop / totalpop * 100
        return accesspop_result

class _AccessPopulationPercentAll(_AccessPopulationPercent):
    def __init__(self, amenity, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=[], worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _AccessPopulationPercentChildren(_AccessPopulationPercent):
    def __init__(self, amenity, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=WorldPopClass.CHILDREN, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _AccessPopulationPercentElderly(_AccessPopulationPercent):
    def __init__(self, amenity, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=WorldPopClass.ELDERLY, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _AccessPopulationPercentFemale(_AccessPopulationPercent):
    def __init__(self, amenity, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=WorldPopClass.FEMALE, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _AccessPopulationPercentInformal(_AccessPopulationPercent):
    def __init__(self, amenity, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=[], worldpop_year=worldpop_year, informal_only=True, **kwargs)



#*********************** openspace ***********************
class AccessToOpenSpace__TotalPopulationPercent(_AccessPopulationPercentAll):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='openspace', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToOpenSpace__ChildrenPercent(_AccessPopulationPercentChildren):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='openspace', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToOpenSpace__ElderlyPercent(_AccessPopulationPercentElderly):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='openspace', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToOpenSpace__FemalePercent(_AccessPopulationPercentFemale):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='openspace', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToOpenSpace__InformalPercent(_AccessPopulationPercentInformal):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='openspace', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)


#*********************** schools ***********************
class AccessToSchools__TotalPopulationPercent(_AccessPopulationPercentAll):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='openspace', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToSchools__ChildrenPercent(_AccessPopulationPercentChildren):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='schools', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToSchools__ElderlyPercent(_AccessPopulationPercentElderly):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='schools', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToSchools__FemalePercent(_AccessPopulationPercentFemale):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='schools', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToSchools__InformalPercent(_AccessPopulationPercentInformal):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='schools', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)


#*********************** goods & services ***********************
class AccessToGoodsAndServices__TotalPopulationPercent(_AccessPopulationPercentAll):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='commerce', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToGoodsAndServices__ChildrenPercent(_AccessPopulationPercentChildren):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='commerce', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToGoodsAndServices__ElderlyPercent(_AccessPopulationPercentElderly):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='commerce', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToGoodsAndServices__FemalePercent(_AccessPopulationPercentFemale):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='commerce', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToGoodsAndServices__InformalPercent(_AccessPopulationPercentInformal):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='commerce', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)


#*********************** potential employment ***********************
class AccessToPotentialEmployment__TotalPopulationPercent(_AccessPopulationPercentAll):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToPotentialEmployment__ChildrenPercent(_AccessPopulationPercentChildren):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToPotentialEmployment__ElderlyPercent(_AccessPopulationPercentElderly):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToPotentialEmployment__FemalePercent(_AccessPopulationPercentFemale):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToPotentialEmployment__InformalPercent(_AccessPopulationPercentInformal):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)


#*********************** public transportation ***********************
class AccessToPublicTransportation__TotalPopulationPercent(_AccessPopulationPercentAll):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='transit', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToPublicTransportation__ChildrenPercent(_AccessPopulationPercentChildren):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='transit', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToPublicTransportation__ElderlyPercent(_AccessPopulationPercentElderly):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='transit', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToPublicTransportation__FemalePercent(_AccessPopulationPercentFemale):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='transit', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToPublicTransportation__InformalPercent(_AccessPopulationPercentInformal):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='transit', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)


#*********************** healthcare ***********************
class AccessToHealthcare__TotalPopulationPercent(_AccessPopulationPercentAll):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='healthcare', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToHealthcare__ChildrenPercent(_AccessPopulationPercentChildren):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='healthcare', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToHealthcare__ElderlyPercent(_AccessPopulationPercentElderly):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='healthcare', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToHealthcare__FemalePercent(_AccessPopulationPercentFemale):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='healthcare', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)

class AccessToHealthcare__InformalPercent(_AccessPopulationPercentInformal):
    def __init__(self, city_id, level, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(amenity='healthcare', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_year=worldpop_year, **kwargs)