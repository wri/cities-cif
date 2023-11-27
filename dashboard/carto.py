from cartoframes.auth import set_default_credentials
from cartoframes import read_carto, to_carto

from typing import List
import numpy as np
import geopandas as gpd
import os
from datetime import datetime
import pandas as pd


def export_results(results: List[gpd.GeoDataFrame], data_to_csv: bool, data_to_carto: bool):
    # set carto credentials
    api_key = os.environ["CARTO_API_KEY"]
    set_default_credentials(username="wri-cities",
                            base_url="https://wri-cities.carto.com/",
                            api_key=api_key)
    # pull indicators table from Carto
    indicators = read_carto('indicators')

    # loop through results tables in the list
    for result in results:
        # convert from wide format to long format
        id_vars = ['geo_id', 'geo_level', 'geo_name', 'geo_parent_name', 'creation_date']
        value_vars = result.columns[-1]
        result_long = result.melt(id_vars=id_vars, value_vars=value_vars, var_name='indicator', value_name='value')

        # set creation_date to today's date
        result_long['creation_date'] = datetime.today().strftime('%Y-%m-%d')

        # set indicator_version to current max plus 1
        indicator_name = result_long['indicator'].unique()[0]
        geo_level = result_long['geo_level'].unique()[0]
        geo_parent_name = result_long['geo_parent_name'].unique()[0]
        latest_indicator_version = indicators[
            (indicators['indicator'] == indicator_name) &
            (indicators['geo_level'] == geo_level) &
            (indicators['geo_parent_name'] == geo_parent_name)
            ]['indicator_version'].max()

        if np.isnan(latest_indicator_version):
            latest_indicator_version = 0

        result_long['indicator_version'] = latest_indicator_version + 1

        # compare results locally
        if data_to_csv == True:
            export_df = pd.concat([indicators[
                                       (indicators['indicator'] == indicator_name) &
                                       (indicators['geo_level'] == geo_level) &
                                       (indicators['geo_parent_name'] == geo_parent_name)
                                       ], result_long], axis=0)

            export_df_wide = pd.pivot(export_df,
                                      index=['geo_id', 'geo_level', 'geo_name', 'geo_parent_name', 'indicator'],
                                      columns='indicator_version', values='value').reset_index()
            # export to csv
            export_df_wide.to_csv(f'{geo_parent_name}_{geo_level}_{indicator_name}.csv')

        # upload valid results to carto
        if data_to_carto == True:
            # upload indicators to carto
            to_carto(result_long, "indicators", if_exists='append')

