from typing import Union
from city_metrix.constants import CSV_FILE_EXTENSION
import pandas as pd
from city_metrix.metrics import Metric
from city_metrix.layers import AccessibleCountPopWeighted, UrbanLandUse, WorldPopClass
from city_metrix.metrix_model import GeoZone

DEFAULT_SPATIAL_RESOLUTION = 100
INFORMAL_CLASS = 3

class _CountAccessiblePopWeighted(Metric):

    def __init__(self, amenity, city_id, level, travel_mode, threshold, unit, project, worldpop_agesex_classes, worldpop_year, informal_only, **kwargs):
        super().__init__(**kwargs)
        self.amenity = amenity
        self.city_id = city_id
        self.level = level
        self.travel_mode = travel_mode
        self.threshold = threshold
        self.unit = unit
        self.project = project
        self.osm_year = 2025
        self.worldpop_agesex_classes = worldpop_agesex_classes
        self.worldpop_year = worldpop_year
        self.informal_only = informal_only

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = DEFAULT_SPATIAL_RESOLUTION) -> Union[pd.DataFrame | pd.Series]:
        count_layer = AccessibleCountPopWeighted(city_id=self.city_id, level=self.level, amenity=self.amenity, travel_mode=self.travel_mode, threshold=self.threshold, unit=self.unit, project=self.project, worldpop_agesex_classes=self.worldpop_agesex_classes, worldpop_year=self.worldpop_year)
        if self.informal_only:
            informal_layer = UrbanLandUse(ulu_class=INFORMAL_CLASS)
            count_layer.masks.append(informal_layer)
        popweighted_count = count_layer.groupby(geo_zone).sum()
        return popweighted_count

class _CountAccessiblePopWeightedAll(_CountAccessiblePopWeighted):
    def __init__(self, city_id, amenity, level, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, project=project, worldpop_agesex_classes=[], worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _CountAccessiblePopWeightedAdults(_CountAccessiblePopWeighted):
    def __init__(self, city_id, amenity, level, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, project=project, worldpop_agesex_classes=WorldPopClass.ADULT, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _CountAccessiblePopWeightedChildren(_CountAccessiblePopWeighted):
    def __init__(self, city_id, amenity, level, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, project=project, worldpop_agesex_classes=WorldPopClass.CHILDREN, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _CountAccessiblePopWeightedElderly(_CountAccessiblePopWeighted):
    def __init__(self, city_id, amenity, level, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, project=project, worldpop_agesex_classes=WorldPopClass.ELDERLY, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _CountAccessiblePopWeightedFemale(_CountAccessiblePopWeighted):
    def __init__(self, city_id, amenity, level, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, project=project, worldpop_agesex_classes=WorldPopClass.FEMALE, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _CountAccessiblePopWeightedInformal(_CountAccessiblePopWeighted):
    def __init__(self, city_id, amenity, level, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, project=project, worldpop_agesex_classes=[], worldpop_year=worldpop_year, informal_only=True, **kwargs)



#************************************************
class CountPotentialEmployers__TotalPopulationPopWeightedCount(_CountAccessiblePopWeightedAll):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["travel_mode", "threshold", "unit"]
    def __init__(self, city_id=None, level=None, travel_mode=None, threshold=None, unit=None, project=None, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, project=project, worldpop_year=worldpop_year, **kwargs)

class CountPotentialEmployers__AdultsPopWeightedCount(_CountAccessiblePopWeightedAdults):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["travel_mode", "threshold", "unit"]
    def __init__(self, city_id=None, level=None, travel_mode=None, threshold=None, unit=None, project=None, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, project=project, worldpop_year=worldpop_year, **kwargs)

class CountPotentialEmployers__FemalePopWeightedCount(_CountAccessiblePopWeightedFemale):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["travel_mode", "threshold", "unit"]
    def __init__(self, city_id=None, level=None, travel_mode=None, threshold=None, unit=None, project=None, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, project=project, worldpop_year=worldpop_year, **kwargs)

class CountPotentialEmployers__InformalPopWeightedCount(_CountAccessiblePopWeightedInformal):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["travel_mode", "threshold", "unit"]
    def __init__(self, city_id=None, level=None, travel_mode=None, threshold=None, unit=None, project=None, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', city_id=city_id, level=level, travel_mode=travel_mode, threshold=threshold, unit=unit, project=project, worldpop_year=worldpop_year, **kwargs)
