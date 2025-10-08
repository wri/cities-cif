import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import GeoZone, Metric
from city_metrix.layers import AcagPM2p5, PopWeightedPM2p5, UrbanLandUse, WorldPopClass

WHO_AQG = 5  # ug/m3  https://www.who.int/publications/i/item/9789240034228


class MeanPM2P5Exposure__MicrogramsPerCubicMeter(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,
                 informal_only=False,
                 **kwargs):
        super().__init__(**kwargs)
        self.informal_only = informal_only
        self.unit = 'micrograms per cubic meter'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:

        pm2p5_layer = AcagPM2p5()

        if self.informal_only:
            informal_layer = UrbanLandUse(ulu_class=3)
            mean_pm2p5 = pm2p5_layer.mask(informal_layer).groupby(geo_zone).mean()
        else:
            mean_pm2p5 = pm2p5_layer.groupby(geo_zone).mean()

        return mean_pm2p5


class MeanPM2P5ExposurePopWeighted__MicrogramsPerCubicMeter(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["year"]

    def __init__(self,
                 year=2023,
                 worldpop_agesex_classes=[],
                 informal_only=False,
                 **kwargs):
        super().__init__(**kwargs)
        self.worldpop_agesex_classes = worldpop_agesex_classes
        self.informal_only = informal_only
        self.year = year
        self.unit = 'micrograms per cubic meter'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        pop_weighted_pm2p5 = PopWeightedPM2p5(acag_year=self.year, worldpop_agesex_classes=self.worldpop_agesex_classes)

        if self.informal_only:
            informal_layer = UrbanLandUse(ulu_class=3)
            mean_pm2p5 = pop_weighted_pm2p5.mask(informal_layer).groupby(geo_zone).mean()
        else:
            mean_pm2p5 = pop_weighted_pm2p5.groupby(geo_zone).mean()

        return mean_pm2p5

class MeanPM2P5ExposurePercentOfWHOGuideline__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,
                 informal_only=False,
                 **kwargs):
        super().__init__(**kwargs)
        self.informal_only = informal_only
        self.unit = 'micrograms per cubic meter'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:

        pm2p5_layer = AcagPM2p5()

        if self.informal_only:
            informal_layer = UrbanLandUse(ulu_class=3)
            mean_pm2p5 = pm2p5_layer.mask(informal_layer).groupby(geo_zone).mean()
        else:
            mean_pm2p5 = pm2p5_layer.groupby(geo_zone).mean()

        if isinstance(mean_pm2p5, pd.DataFrame):
            result = mean_pm2p5.copy()
            result['value'] = 100 * mean_pm2p5['value'] / WHO_AQG
        else:
            result = 100 * mean_pm2p5 / WHO_AQG

        return result


class MeanPM2P5ExposurePopWeightedPercentOfWHOGuideline__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["year"]

    def __init__(self,
                 year=2023,
                 worldpop_agesex_classes=[],
                 informal_only=False,
                 **kwargs):
        super().__init__(**kwargs)
        self.worldpop_agesex_classes = worldpop_agesex_classes
        self.informal_only = informal_only
        self.year = year
        self.unit = 'micrograms per cubic meter'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        pop_weighted_pm2p5 = PopWeightedPM2p5(acag_year=self.year, worldpop_agesex_classes=self.worldpop_agesex_classes)

        if self.informal_only:
            informal_layer = UrbanLandUse(ulu_class=3)
            mean_pm2p5 = pop_weighted_pm2p5.mask(informal_layer).groupby(geo_zone).mean()
        else:
            mean_pm2p5 = pop_weighted_pm2p5.groupby(geo_zone).mean()

        if isinstance(mean_pm2p5, pd.DataFrame):
            result = mean_pm2p5.copy()
            result['value'] = 100 * mean_pm2p5['value'] / WHO_AQG
        else:
            result = 100 * mean_pm2p5 / WHO_AQG

        return result


class MeanPM2P5ExposurePopWeightedChildren__MicrogramsPerCubicMeter(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["year"]

    def __init__(self, year=2023, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.unit = 'micrograms per cubic meter'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        pop_weighted_pm2p5_children = (MeanPM2P5ExposurePopWeighted__MicrogramsPerCubicMeter(year=self.year,
                                                                                             worldpop_agesex_classes=WorldPopClass.CHILDREN,
                                                                                             informal_only=False))

        return pop_weighted_pm2p5_children.get_metric(geo_zone=geo_zone)


class MeanPM2P5ExposurePopWeightedElderly__MicrogramsPerCubicMeter(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["year"]

    def __init__(self, year=2023, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.unit = 'micrograms per cubic meter'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        pop_weighted_pm2p5_elderly = (MeanPM2P5ExposurePopWeighted__MicrogramsPerCubicMeter(year=self.year,
                                                                                            worldpop_agesex_classes=WorldPopClass.ELDERLY,
                                                                                            informal_only=False))

        return pop_weighted_pm2p5_elderly.get_metric(geo_zone=geo_zone)


class MeanPM2P5ExposurePopWeightedFemale__MicrogramsPerCubicMeter(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["year"]

    def __init__(self, year=2023, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.unit = 'micrograms per cubic meter'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        pop_weighted_pm2p5_female = (MeanPM2P5ExposurePopWeighted__MicrogramsPerCubicMeter(year=self.year,
                                                                                           worldpop_agesex_classes=WorldPopClass.FEMALE,
                                                                                           informal_only=False))

        return pop_weighted_pm2p5_female.get_metric(geo_zone=geo_zone)


class MeanPM2P5ExposurePopWeightedInformal__MicrogramsPerCubicMeter(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["year"]

    def __init__(self, year=2023, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.unit = 'micrograms per cubic meter'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        pop_weighted_pm2p5_informal = (MeanPM2P5ExposurePopWeighted__MicrogramsPerCubicMeter(year=self.year,
                                                                                             worldpop_agesex_classes=[],
                                                                                             informal_only=True))

        return pop_weighted_pm2p5_informal.get_metric(geo_zone=geo_zone)


#***************************************** Outputs as percent of WHO guideline *************************************


class MeanPM2P5ExposurePopWeightedPercentOfWHOGuidelineTotalPopulation__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["year"]

    def __init__(self, year=2023, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.unit = 'percent of WHO guideline'
    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        pop_weighted_pm2p5_children = (MeanPM2P5ExposurePopWeightedPercentOfWHOGuideline__Percent(year=self.year,
                                                                                             worldpop_agesex_classes=[],
                                                                                             informal_only=False))

        return pop_weighted_pm2p5_children.get_metric(geo_zone=geo_zone)

class MeanPM2P5ExposurePopWeightedPercentOfWHOGuidelineChildren__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["year"]

    def __init__(self, year=2023, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.unit = 'percent of WHO guideline'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        pop_weighted_pm2p5_children = (MeanPM2P5ExposurePopWeightedPercentOfWHOGuideline__Percent(year=self.year,
                                                                                             worldpop_agesex_classes=WorldPopClass.CHILDREN,
                                                                                             informal_only=False))

        return pop_weighted_pm2p5_children.get_metric(geo_zone=geo_zone)


class MeanPM2P5ExposurePopWeightedPercentOfWHOGuidelineElderly__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["year"]

    def __init__(self, year=2023, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.unit = 'percent of WHO guideline'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        pop_weighted_pm2p5_elderly = (MeanPM2P5ExposurePopWeightedPercentOfWHOGuideline__Percent(year=self.year,
                                                                                            worldpop_agesex_classes=WorldPopClass.ELDERLY,
                                                                                            informal_only=False))

        return pop_weighted_pm2p5_elderly.get_metric(geo_zone=geo_zone)


class MeanPM2P5ExposurePopWeightedPercentOfWHOGuidelineFemale__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["year"]

    def __init__(self, year=2023, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.unit = 'percent of WHO guideline'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        pop_weighted_pm2p5_female = (MeanPM2P5ExposurePopWeightedPercentOfWHOGuideline__Percent(year=self.year,
                                                                                           worldpop_agesex_classes=WorldPopClass.FEMALE,
                                                                                           informal_only=False))

        return pop_weighted_pm2p5_female.get_metric(geo_zone=geo_zone)


class MeanPM2P5ExposurePopWeightedPercentOfWHOGuidelineInformal__Percent(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["year"]

    def __init__(self, year=2023, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.unit = 'percent of WHO guideline'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        pop_weighted_pm2p5_informal = (MeanPM2P5ExposurePopWeightedPercentOfWHOGuideline__Percent(year=self.year,
                                                                                             worldpop_agesex_classes=[],
                                                                                             informal_only=True))

        return pop_weighted_pm2p5_informal.get_metric(geo_zone=geo_zone)