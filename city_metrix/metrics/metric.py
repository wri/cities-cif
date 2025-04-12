import os
from abc import abstractmethod
from pathlib import Path

import geopandas as gpd
import pandas as pd
from geopandas import GeoDataFrame
from pandas import Series, DataFrame

from city_metrix import AIRTABLE_PERSONAL_API_KEY, AIRTABLE_METRICS_BASE_ID
from city_metrix.metrics.metric_geometry import GeoZone
from city_metrix.metrix_dao import write_geojson, write_csv


class Metric():
    def __init__(self, layer=None):
        self.layer = layer
        if layer is None:
            self.layer = self

    @abstractmethod
    def get_data(self, geo_zone: GeoZone, spatial_resolution:int) -> pd.Series:
        """
        Construct polygonal dataset using baser layers
        :return: A rioxarray-format GeoPandas DataFrame
        """
        ...

    def write_to_db(self, geo_zone: GeoZone, output_path:str, spatial_resolution:int = None, **kwargs):
        """
        Write the metric to a path. Does not apply masks.
        :return:
        """
        # _verify_extension(output_path, '.geojson')

        indicator = self.layer.get_data(geo_zone, spatial_resolution)

        if isinstance(indicator, Series) and indicator.name is None:
            # TODO: after CDB-257 is fixed, replace with Exception
            # raise Exception("Series must have a name.")
            indicator.name = 'indicator'

        if isinstance(indicator, (pd.Series, pd.DataFrame)):
            from pyairtable import Table
            api_key = AIRTABLE_PERSONAL_API_KEY
            base_id = AIRTABLE_METRICS_BASE_ID
            table = Table(api_key, base_id, 'metrics')

            gdf = pd.concat([geo_zone, indicator], axis=1)
            cols = gdf.columns.values.tolist()
            exclude_values = {'index', 'geometry'}
            filtered_list = [item for item in cols if item not in exclude_values]

            from shapely.wkt import dumps
            for index, row in gdf.iterrows():
                geom = row['geometry'].wkt
                for col in filtered_list:
                    id = f"test{index}"
                    value = row[col]
                    fields = {"city_metric_id":id, "geometry":geom, "attribute":col, "value": value}

                    table.create(fields=fields)

        else:
            raise NotImplementedError("Can only write Series or Dataframe Indicator data")


    def write_as_geojson(self, geo_zones: GeoZone, output_path:str, spatial_resolution:int = None, **kwargs):
        """
        Write the metric to a path. Does not apply masks.
        :return:
        """
        _verify_extension(output_path, '.geojson')

        indicator = self.layer.get_data(geo_zones, spatial_resolution)

        if isinstance(indicator, Series) and indicator.name is None:
            # TODO: after CDB-257 is fixed, replace with Exception
            # raise Exception("Series must have a name.")
            indicator.name = 'indicator'

        if isinstance(indicator, (pd.Series, pd.DataFrame)):
            gdf = pd.concat([geo_zones.zones, indicator], axis=1)
            write_geojson(gdf, output_path)
        else:
            raise NotImplementedError("Can only write Series or Dataframe Indicator data")

    def write_as_csv(self, geo_zone: GeoZone, output_path: str, spatial_resolution:int = None, **kwargs):
        """
        Write the metric to a path. Does not apply masks.
        :return:
        """
        _verify_extension(output_path, '.csv')

        indicator = self.layer.get_data(geo_zone, spatial_resolution)

        if isinstance(indicator, Series) and indicator.name is None:
            # TODO: after CDB-257 is fixed, replace with Exception
            # raise Exception("Series must have a name.")
            indicator.name = 'indicator'

        if isinstance(indicator, (pd.Series, pd.DataFrame)):
            write_csv(indicator, output_path)
        else:
            raise NotImplementedError("Can only write Series or Dataframe Indicator data")


def _verify_extension(file_path, extension):
    if Path(file_path).suffix != extension:
        raise ValueError(f"File name must have '{extension}' extension")
