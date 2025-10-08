import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrics import Metric
from city_metrix.layers import AccessibleCount, AccessibleCountPopWeighted, UrbanLandUse, WorldPop, WorldPopClass
from city_metrix.metrix_model import GeoZone

DEFAULT_SPATIAL_RESOLUTION = 100
INFORMAL_CLASS = 3


class _CountAccessiblePopWeighted(Metric):
    def __init__(self, amenity, travel_mode, threshold, unit, project, worldpop_agesex_classes, worldpop_year, informal_only, **kwargs):
        super().__init__(**kwargs)
        self.amenity = amenity
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
                   spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION) -> Union[pd.DataFrame | pd.Series]:
    
        city_id = geo_zone.city_id
        level = {'city_admin_level': 'adminbound',
                 'urban_extent': 'urbextbound'}[geo_zone.aoi_id]

        count_layer = AccessibleCountPopWeighted(city_id=city_id, level=level, amenity=self.amenity, travel_mode=self.travel_mode, threshold=self.threshold,
                                                 unit=self.unit, project=self.project, worldpop_agesex_classes=self.worldpop_agesex_classes, worldpop_year=self.worldpop_year)
        if self.informal_only:
            informal_layer = UrbanLandUse(ulu_class=INFORMAL_CLASS)
            count_layer.masks.append(informal_layer)
        popweighted_count = count_layer.groupby(geo_zone).sum()

        return popweighted_count

class _CountAccessiblePerCapita(Metric):
    def __init__(self, amenity, travel_mode, threshold, unit, project, worldpop_agesex_classes, worldpop_year, informal_only, **kwargs):
        super().__init__(**kwargs)
        self.amenity = amenity
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
                   spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION) -> Union[pd.DataFrame | pd.Series]:

        count_layer = AccessibleCount(city_id=city_id, level=level, amenity=self.amenity, travel_mode=self.travel_mode, threshold=self.threshold,
                                                 unit=self.unit, project=self.project)
        population_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes, year=self.worldpop_year)
        if self.informal_only:
            informal_layer = UrbanLandUse(ulu_class=INFORMAL_CLASS)
            count_layer = count_layer.mask(informal_layer)
            population_layer = population_layer.mask(informal_layer)

        count = count_layer.groupby(geo_zone).sum()
        population = population_layer.groupby(geo_zone).sum()

        if isinstance(count, pd.DataFrame):
            result = count.copy()
            result['value'] = count['value'] / population['value']
        else:
            result = count / population

        return result


class _CountAccessiblePopWeightedAll(_CountAccessiblePopWeighted):
    def __init__(self, amenity, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, travel_mode=travel_mode, threshold=threshold,
                         unit=unit, project=project, worldpop_agesex_classes=[], worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _CountAccessiblePopWeightedAdults(_CountAccessiblePopWeighted):
    def __init__(self, amenity, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, travel_mode=travel_mode, threshold=threshold, unit=unit,
                         project=project, worldpop_agesex_classes=WorldPopClass.ADULT, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _CountAccessiblePopWeightedChildren(_CountAccessiblePopWeighted):
    def __init__(self, amenity, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, travel_mode=travel_mode, threshold=threshold, unit=unit,
                         project=project, worldpop_agesex_classes=WorldPopClass.CHILDREN, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _CountAccessiblePopWeightedElderly(_CountAccessiblePopWeighted):
    def __init__(self, amenity, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, travel_mode=travel_mode, threshold=threshold, unit=unit,
                         project=project, worldpop_agesex_classes=WorldPopClass.ELDERLY, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _CountAccessiblePopWeightedFemale(_CountAccessiblePopWeighted):
    def __init__(self, amenity, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, travel_mode=travel_mode, threshold=threshold, unit=unit,
                         project=project, worldpop_agesex_classes=WorldPopClass.FEMALE, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _CountAccessiblePopWeightedInformal(_CountAccessiblePopWeighted):
    def __init__(self, amenity, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, travel_mode=travel_mode, threshold=threshold,
                         unit=unit, project=project, worldpop_agesex_classes=[], worldpop_year=worldpop_year, informal_only=True, **kwargs)

class _CountAccessiblePerCapitaAll(_CountAccessiblePerCapita):
    def __init__(self, amenity, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, travel_mode=travel_mode, threshold=threshold,
                         unit=unit, project=project, worldpop_agesex_classes=[], worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _CountAccessiblePerCapitaAdults(_CountAccessiblePerCapita):
    def __init__(self, amenity, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, travel_mode=travel_mode, threshold=threshold, unit=unit,
                         project=project, worldpop_agesex_classes=WorldPopClass.ADULT, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _CountAccessiblePerCapitaChildren(_CountAccessiblePerCapita):
    def __init__(self, amenity, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, travel_mode=travel_mode, threshold=threshold, unit=unit,
                         project=project, worldpop_agesex_classes=WorldPopClass.CHILDREN, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _CountAccessiblePerCapitaElderly(_CountAccessiblePerCapita):
    def __init__(self, amenity, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, travel_mode=travel_mode, threshold=threshold, unit=unit,
                         project=project, worldpop_agesex_classes=WorldPopClass.ELDERLY, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _CountAccessiblePerCapitaFemale(_CountAccessiblePerCapita):
    def __init__(self, amenity, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, travel_mode=travel_mode, threshold=threshold, unit=unit,
                         project=project, worldpop_agesex_classes=WorldPopClass.FEMALE, worldpop_year=worldpop_year, informal_only=False, **kwargs)

class _CountAccessiblePerCapitaInformal(_CountAccessiblePerCapita):
    def __init__(self, amenity, travel_mode, threshold, unit, project, worldpop_year=2020, **kwargs):
        super().__init__(amenity=amenity, travel_mode=travel_mode, threshold=threshold,
                         unit=unit, project=project, worldpop_agesex_classes=[], worldpop_year=worldpop_year, informal_only=True, **kwargs)


# ************************************************
class CountPotentialEmployersTotalPopulationPopWeighted__Count(_CountAccessiblePopWeightedAll):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["travel_mode", "threshold", "unit"]

    def __init__(self, travel_mode=None, threshold=None, unit=None, project=None, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', travel_mode=travel_mode,
                         threshold=threshold, unit=unit, project=project, worldpop_year=worldpop_year, **kwargs)


class CountPotentialEmployersAdultsPopWeighted__Count(_CountAccessiblePopWeightedAdults):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["travel_mode", "threshold", "unit"]

    def __init__(self, travel_mode=None, threshold=None, unit=None, project=None, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', travel_mode=travel_mode,
                         threshold=threshold, unit=unit, project=project, worldpop_year=worldpop_year, **kwargs)


class CountPotentialEmployersChildrenPopWeighted__Count(_CountAccessiblePopWeightedChildren):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["travel_mode", "threshold", "unit"]

    def __init__(self, travel_mode=None, threshold=None, unit=None, project=None, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', travel_mode=travel_mode,
                         threshold=threshold, unit=unit, project=project, worldpop_year=worldpop_year, **kwargs)


class CountPotentialEmployersElderlyPopWeighted__Count(_CountAccessiblePopWeightedElderly):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["travel_mode", "threshold", "unit"]

    def __init__(self, travel_mode=None, threshold=None, unit=None, project=None, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', travel_mode=travel_mode,
                         threshold=threshold, unit=unit, project=project, worldpop_year=worldpop_year, **kwargs)


class CountPotentialEmployersFemalePopWeighted__Count(_CountAccessiblePopWeightedFemale):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["travel_mode", "threshold", "unit"]

    def __init__(self, travel_mode=None, threshold=None, unit=None, project=None, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', travel_mode=travel_mode,
                         threshold=threshold, unit=unit, project=project, worldpop_year=worldpop_year, **kwargs)


class CountPotentialEmployersInformalPopWeighted__Count(_CountAccessiblePopWeightedInformal):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["travel_mode", "threshold", "unit"]

    def __init__(self, travel_mode=None, threshold=None, unit=None, project=None, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', travel_mode=travel_mode,
                         threshold=threshold, unit=unit, project=project, worldpop_year=worldpop_year, **kwargs)


class CountPotentialEmployersPerCapitaTotalPopulation__CountPerPerson(_CountAccessiblePerCapitaAll):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["travel_mode", "threshold", "unit"]

    def __init__(self, travel_mode=None, threshold=None, unit=None, project=None, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', travel_mode=travel_mode,
                         threshold=threshold, unit=unit, project=project, worldpop_year=worldpop_year, **kwargs)


class CountPotentialEmployersPerCapitaAdult__CountPerPerson(_CountAccessiblePerCapitaAdults):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["travel_mode", "threshold", "unit"]

    def __init__(self, travel_mode=None, threshold=None, unit=None, project=None, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', travel_mode=travel_mode,
                         threshold=threshold, unit=unit, project=project, worldpop_year=worldpop_year, **kwargs)


class CountPotentialEmployersPerCapitaChildren__CountPerPerson(_CountAccessiblePerCapitaChildren):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["travel_mode", "threshold", "unit"]

    def __init__(self, travel_mode=None, threshold=None, unit=None, project=None, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', travel_mode=travel_mode,
                         threshold=threshold, unit=unit, project=project, worldpop_year=worldpop_year, **kwargs)


class CountPotentialEmployersPerCapitaElderly__CountPerPerson(_CountAccessiblePerCapitaElderly):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["travel_mode", "threshold", "unit"]

    def __init__(self, travel_mode=None, threshold=None, unit=None, project=None, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', travel_mode=travel_mode,
                         threshold=threshold, unit=unit, project=project, worldpop_year=worldpop_year, **kwargs)


class CountPotentialEmployersPerCapitaFemale__CountPerPerson(_CountAccessiblePerCapitaFemale):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["travel_mode", "threshold", "unit"]

    def __init__(self, travel_mode=None, threshold=None, unit=None, project=None, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', travel_mode=travel_mode,
                         threshold=threshold, unit=unit, project=project, worldpop_year=worldpop_year, **kwargs)


class CountPotentialEmployersPerCapitaInformal__CountPerPerson(_CountAccessiblePerCapitaInformal):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["travel_mode", "threshold", "unit"]

    def __init__(self, travel_mode=None, threshold=None, unit=None, project=None, worldpop_year=2020, **kwargs):
        super().__init__(amenity='economic', travel_mode=travel_mode,
                         threshold=threshold, unit=unit, project=project, worldpop_year=worldpop_year, **kwargs)
