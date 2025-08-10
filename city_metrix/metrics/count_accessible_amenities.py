from geopandas import GeoDataFrame, GeoSeries
from pandas import Series
from city_metrix.metrics import Metric
from city_metrix.layers import WorldPopClass
from math import floor
import shapely

DEFAULT_SPATIAL_RESOLUTION = 100

class CountAccessiblePopWeighted(Metric):
    def __init__(self, amenity, city_id, level, travel_mode, threshold, unit, worldpop_agesex_classes, worldpop_year, informal_only, **kwargs):
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
        count_layer = AccessibleCountPopWeighted(city_id=self.city_id, level=self.level, amenity=self.amenity, travel_mode=self.travel_mode, threshold=self.threshold, unit=self.unit, worldpop_agesex_classes=self.worldpop_agesex_classes, worldpop_year=self.worldpop_year)
        zones = zones.reset_index()
        return count_layer.groupby(zones).sum()

class CountAccessiblePopWeightedAll(CountAccessiblePopWeighted):
    def __init__(self, city_id='KEN-Nairobi', level='adminbound',  amenity='economic', travel_mode='walk', threshold=15, unit='minutes', worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=[], worldpop_year=worldpop_year, informal_only=False, **kwargs)

class CountAccessiblePopWeightedAdults(CountAccessiblePopWeighted):
    def __init__(self, city_id='KEN-Nairobi', level='adminbound', amenity='economic', travel_mode='walk', threshold=15, unit='minutes', worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=WorldPopClass.ADULTS, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class CountAccessiblePopWeightedChildren(CountAccessiblePopWeighted):
    def __init__(self, city_id='KEN-Nairobi', level='adminbound', amenity='economic', travel_mode='walk', threshold=15, unit='minutes', worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=WorldPopClass.CHILDREN, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class CountAccessiblePopWeightedElderly(CountAccessiblePopWeighted):
    def __init__(self, city_id='KEN-Nairobi', level='adminbound', amenity='economic', travel_mode='walk', threshold=15, unit='minutes', worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=WorldPopClass.ELDERLY, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class CountAccessiblePopWeightedFemale(CountAccessiblePopWeighted):
    def __init__(self, city_id='KEN-Nairobi', level='adminbound', amenity='economic', travel_mode='walk', threshold=15, unit='minutes', worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=WorldPopClass.FEMALE, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class CountAccessiblePopWeightedInformal(CountAccessiblePopWeighted):
    def __init__(self, city_id='KEN-Nairobi', level='adminbound', amenity='economic', travel_mode='walk', threshold=15, unit='minutes', worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, worldpop_agesex_classes=[], worldpop_year=worldpop_year, informal_only=True, **kwargs)