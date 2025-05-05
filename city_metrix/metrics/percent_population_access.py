from geopandas import GeoDataFrame, GeoSeries
from city_metrix.layers.layer_geometry import GeoExtent
from pandas import Series
import shapely
from city_metrix.metrics import Metric
from city_metrix.layers.isoline import AccessibleRegion
from city_metrix.layers.world_pop import WorldPop, WorldPopClass
from city_metrix.layers.urban_land_use import UrbanLandUse

class AccessPopulationPercent(Metric):
    def __init__(self, city_id, level, amenity, travel_mode, threshold, unit, worldpop_agesex_classes=[], worldpop_year=2020, informal_only=False, **kwargs):
        super().__init__(**kwargs)
        self.city_id = city_id
        self.level = level
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
        iso_layer = AccessibleRegion(city_id=self.city_id, amenity=self.amenity, travel_mode=self.travel_mode, threshold=self.threshold, unit=self.unit)
        iso_data = iso_layer.get_data(GeoExtent(zones.total_bounds))
        accesspop_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes, year=self.worldpop_year, masks=[iso_layer,])
        totalpop_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes, year=self.worldpop_year)
        if self.informal_only:
            informal_layer = UrbanLandUse(ulu_class=3)
            accesspop_layer.masks.append(informal_layer)
            totalpop_layer.masks.append(informal_layer)
        zones_reset = zones.reset_index()
        return 100 * accesspop_layer.groupby(zones_reset).sum() / totalpop_layer.groupby(zones_reset).sum()

class AccessPopulationPercentAll(AccessPopulationPercent):
    def __init__(self, city_id, level, amenity, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(city_id=city_id, level=level, amenity=amenity, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=[], worldpop_year=worldpop_year, informal_only=False, **kwargs)

class AccessPopulationPercentChildren(AccessPopulationPercent):
    def __init__(self, city_id, level, amenity, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(city_id=city_id, level=level, amenity=amenity, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=WorldPopClass.CHILDREN, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class AccessPopulationPercentElderly(AccessPopulationPercent):
    def __init__(self, city_id, level, amenity, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(city_id=city_id, level=level, amenity=amenity, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=WorldPopClass.ELDERLY, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class AccessPopulationPercentFemale(AccessPopulationPercent):
    def __init__(self, city_id, level, amenity, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(city_id=city_id, level=level, amenity=amenity, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=WorldPopClass.FEMALE, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class AccessPopulationPercentInformal(AccessPopulationPercent):
    def __init__(self, city_id, level, amenity, travel_mode, threshold, unit, worldpop_year=2020, **kwargs):
        super().__init__(city_id=city_id, level=level, amenity=amenity, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=[], worldpop_year=worldpop_year, informal_only=True, **kwargs)
