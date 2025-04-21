import os
from abc import abstractmethod
from pathlib import Path

import geopandas as gpd
import pandas as pd
from geopandas import GeoDataFrame
from pandas import Series, DataFrame


class Metric():
    def __init__(self, aggregate=None):
        self.aggregate = aggregate
        if aggregate is None:
            self.aggregate = self

    @abstractmethod
    def get_data(self, zones: GeoDataFrame, spatial_resolution:int) -> gpd.GeoSeries:
        """
        Construct polygonal dataset using baser layers
        :return: A rioxarray-format GeoPandas DataFrame
        """
        ...

    def write_as_geojson(self, zones: GeoDataFrame, output_path:str, spatial_resolution:int = None, **kwargs):
        """
        Write the metric to a path. Does not apply masks.
        :return:
        """
        _verify_extension(output_path, '.geojson')

        indicator = self.aggregate.get_data(zones, spatial_resolution)

        if isinstance(indicator, Series) and indicator.name is None:
            # TODO: after CDB-257 is fixed, replace with Exception
            # raise Exception("Series must have a name.")
            indicator.name = 'indicator'

        if isinstance(indicator, (pd.Series, pd.DataFrame)):
            gdf = pd.concat([zones, indicator], axis=1)
            gdf.to_file(output_path, driver="GeoJSON")
        else:
            raise NotImplementedError("Can only write Series or Dataframe Indicator data")

    def write_as_csv(self, zones: GeoDataFrame, output_path: str, spatial_resolution:int = None, **kwargs):
        """
        Write the metric to a path. Does not apply masks.
        :return:
        """
        _verify_extension(output_path, '.csv')

        indicator = self.aggregate.get_data(zones, spatial_resolution)

        if isinstance(indicator, Series) and indicator.name is None:
            # TODO: after CDB-257 is fixed, replace with Exception
            # raise Exception("Series must have a name.")
            indicator.name = 'indicator'

        if isinstance(indicator, (pd.Series, pd.DataFrame)):
            indicator.to_csv(output_path, header=True, index=True, index_label='index')
        else:
            raise NotImplementedError("Can only write Series or Dataframe Indicator data")


def _verify_extension(file_path, extension):
    if Path(file_path).suffix != extension:
        raise ValueError(f"File name must have '{extension}' extension")
