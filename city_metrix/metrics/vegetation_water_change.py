import pandas as pd
from typing import Union

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import GeoZone, Metric
from city_metrix.layers import VegetationWaterMap


DEFAULT_SPATIAL_RESOLUTION = 10

# TODO: layer generation and zonal stats use different spatial resolutions


class VegetationWaterChangeGainArea__SquareMeters(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["start_date", "end_date"]

    def __init__(self, start_date="2016-01-01", end_date="2022-12-31", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.unit = 'square meters'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution=DEFAULT_SPATIAL_RESOLUTION) -> Union[pd.DataFrame | pd.Series]:
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        gain_counts = VegetationWaterMap(start_date=self.start_date, end_date=self.end_date, greenwater_layer='gaingreenwaterSlope').groupby(geo_zone).count()

        if isinstance(gain_counts, pd.DataFrame):
            result = gain_counts.copy()
            result['value'] = gain_counts['value'] * spatial_resolution ** 2
        else:
            result = gain_counts * spatial_resolution ** 2

        return result


class VegetationWaterChangeLossArea__SquareMeters(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["start_date", "end_date"]

    def __init__(self, start_date="2016-01-01", end_date="2022-12-31", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.unit = 'square meters'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution=DEFAULT_SPATIAL_RESOLUTION) -> Union[pd.DataFrame | pd.Series]:
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        loss_counts = VegetationWaterMap(start_date=self.start_date, end_date=self.end_date, greenwater_layer='lossgreenwaterSlope').groupby(geo_zone).count()

        if isinstance(loss_counts, pd.DataFrame):
            result = loss_counts.copy()
            result['value'] = loss_counts['value'] * spatial_resolution ** 2
        else:
            result = loss_counts * spatial_resolution ** 2

        return result


class VegetationWaterChangeGainLoss__Ratio(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["start_date", "end_date"]

    def __init__(self, start_date="2016-01-01", end_date="2022-12-31", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.unit = 'ratio'

    def get_metric(self,
                   geo_zone: GeoZone,
                   spatial_resolution: int = None) -> Union[pd.DataFrame | pd.Series]:
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        start_counts = VegetationWaterMap(start_date=self.start_date, end_date=self.end_date, greenwater_layer='startgreenwaterIndex').groupby(geo_zone).count()
        loss_counts = VegetationWaterMap(start_date=self.start_date, end_date=self.end_date, greenwater_layer='lossgreenwaterSlope').groupby(geo_zone).count()
        gain_counts = VegetationWaterMap(start_date=self.start_date, end_date=self.end_date, greenwater_layer='gaingreenwaterSlope').groupby(geo_zone).count()

        if isinstance(gain_counts, pd.DataFrame):
            result = gain_counts.copy()
            result['value'] = (gain_counts['value'] - loss_counts['value']) / start_counts['value']
        else:
            result = (gain_counts - loss_counts) / start_counts

        return result
