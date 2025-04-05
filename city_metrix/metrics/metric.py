import os
from abc import abstractmethod

import geopandas as gpd
import pandas as pd
from geopandas import GeoDataFrame
from pandas import Series, DataFrame


class Metric():
    def __init__(self, aggregate=None, masks=[]):
        self.aggregate = aggregate
        if aggregate is None:
            self.aggregate = self

        self.masks = masks

    @abstractmethod
    def get_data(self, zones: GeoDataFrame) -> gpd.GeoSeries:
        """
        Construct polygonal dataset using baser layers
        :return: A rioxarray-format GeoPandas DataFrame
        """
        ...

    def write(self, zones: GeoDataFrame, output_path:str, **kwargs):
        """
        Write the metric to a path. Does not apply masks.
        :return:
        """
        indicator = self.aggregate.get_data(zones)

        if isinstance(indicator, Series) or isinstance(indicator, DataFrame):
            if isinstance(indicator, Series) and indicator.name is None:
                indicator.name = 'indicator'

            gdf = pd.concat([zones, indicator], axis=1)

            gdf.to_file(output_path, driver="GeoJSON")
        else:
            raise NotImplementedError("Can only write Series or Dataframe Indicator data")


