from geopandas import GeoDataFrame, GeoSeries
from pandas import Series
import shapely

from city_metrix.layers.isoline import Isoline
from city_metrix.layers.world_pop import WorldPop
from city_metrix.layers.urban_land_use import UrbanLandUse
from city_metrix.layers.layer import Layer, get_utm_zone_epsg


class AccessPopulationPercent(Metric):

    def __init__(self, city_id, amenity, travel_mode, threshold, unit, worldpop_agesex_classes=[], worldpop_year=2020, informal_only=False, **kwargs):
        super().__init__(**kwargs)
        self.city_id = city_id
        self.amenity = amenity
        self.travel_mode = travel_mode
        self.threshold = threshold
        self.unit = unit
        self.worldpop_agesex_classes = worldpop_agesex_classes
        self.worldpop_year = worldpop_year
        self.informal_only = informal_only

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:

        iso_layer = AccessibleRegion(amenity=self.amenity, travel_mode=self.travel_mode, threshold=self.threshold, unit=self.unit)
        iso_data = iso_layer.get_data(city_id)
        accesspop_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes, year=self.worldpop_year, masks=[iso_layer,])
        totalpop_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes, year=self.worldpop_year)
        if informal_only:
            informal_layer = UrbanLandUse(return_value=3)
            accesspop_layer.masks.append(informal_layer)
            totalpop_layer.masks.append(informal_layer)
        res = []
        zones_reset = zones.reset_index()
        for rownum in range(len(zones_reset)):  # Doing it district-by-district to avoid empty-GDF error
            try:
                res.append(100 * accesspop_layer.groupby(zones_reset.iloc[[rownum]]).sum()[0] / totalpop_layer.groupby(zones_reset.iloc[[rownum]]).sum()[0])
            except:
                res.append(0)
        result = Series(res)
        return result


class AccessPopulationPercentAll(AccessPopulationPercent):
    def __init__(self, city_id, amenity, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        self.city_id = city_id
        self.amenity = amenity
        self.travel_mode = travel_mode
        self.threshold = threshold
        self.unit = unit
        self.worldpop_agesex_classes = []
        self.worldpop_year = worldpop_year
        self.informal_only = False

class AccessPopulationPercentChildren(AccessPopulationPercent):
    def __init__(self, city_id, amenity, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        self.city_id = city_id
        self.amenity = amenity
        self.travel_mode = travel_mode
        self.threshold = threshold
        self.unit = unit
        self.worldpop_agesex_classes = [WorldPopClass.CHILDREN]
        self.worldpop_year = worldpop_year
        self.informal_only = False

class AccessPopulationPercentElderly(AccessPopulationPercent):
    def __init__(self, city_id, amenity, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        self.city_id = city_id
        self.amenity = amenity
        self.travel_mode = travel_mode
        self.threshold = threshold
        self.unit = unit
        self.worldpop_agesex_classes = [WorldPopClass.ELDERLY]
        self.worldpop_year = worldpop_year
        self.informal_only = False

class AccessPopulationPercentFemale(AccessPopulationPercent):
    def __init__(self, city_id, amenity, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        self.city_id = city_id
        self.amenity = amenity
        self.travel_mode = travel_mode
        self.threshold = threshold
        self.unit = unit
        self.worldpop_agesex_classes = [WorldPopClass.FEMALE]
        self.worldpop_year = worldpop_year
        self.informal_only = False

class AccessPopulationPercentChildren(AccessPopulationPercent):
    def __init__(self, city_id, amenity, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        self.city_id = city_id
        self.amenity = amenity
        self.travel_mode = travel_mode
        self.threshold = threshold
        self.unit = unit
        self.worldpop_agesex_classes = []
        self.worldpop_year = worldpop_year
        self.informal_only = True
