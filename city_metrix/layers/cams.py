import cdsapi
import os
import datetime
import numpy as np
import xarray as xr
import glob
from enum import Enum

from .layer import Layer
from .layer_dao import retrieve_cached_city_data
from .layer_geometry import GeoExtent
from ..constants import NETCDF_FILE_EXTENSION


class CamsSpecies(Enum):
    NO2 = {
        'name': 'nitrogen dioxide',
        'molar_mass': 46.0055,
        'who_threshold': 25.0,
        'cost_per_tonne': 67000,
        'eac4_varname': 'no2'
    }
    SO2 = {
        'name': 'sulfur dioxide',
        'molar_mass': 64.066,
        'who_threshold': 40.0,
        'cost_per_tonne': 33000,
        'eac4_varname': 'so2'
    }
    O3 = {    # Ozone thresholds are based on 8-hour average, not 24-hour.
        'name': 'ozone',
        'molar_mass': 48.0,
        'who_threshold': 100.0,
        'cost_per_tonne': np.nan,
        'eac4_varname': 'go3'
    }
    PM25 = {
        'name': 'fine particulate matter',
        'who_threshold': 15.0,
        'cost_per_tonne': np.nan,
        'eac4_varname': 'pm2p5'
    }
    PM10 = {
        'name': 'coarse particulate matter',
        'who_threshold': 45.0,
        'cost_per_tonne': np.nan,
        'eac4_varname': 'pm10'
    },
    CO = {
        'name': 'carbon monoxide',
        'molar_mass': 28.01,
        'who_threshold': 4000.0,
        'cost_per_tonne': 250,
        'eac4_varname': 'co'
    }


class Cams(Layer):
    OUTPUT_FILE_FORMAT = NETCDF_FILE_EXTENSION
    MAJOR_LAYER_NAMING_ATTS = None
    MINOR_LAYER_NAMING_ATTS = None

    def __init__(self, start_date="2023-01-01", end_date="2023-12-31", species=[], **kwargs):
        """
        Attributes:
            start_date: starting date for data retrieval
            end_date: ending date for data retrieval
        """
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.species = species

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None,
                 allow_cache_retrieval=False):
        #Note: spatial_resolution and resampling_method arguments are ignored.

        # Attempt to retrieve cached file based on layer_id.
        retrieved_cached_data = retrieve_cached_city_data(self, bbox, allow_cache_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        min_lon, min_lat, max_lon, max_lat = bbox.as_geographic_bbox().bounds

        c = cdsapi.Client(url='https://ads.atmosphere.copernicus.eu/api')
        timestamp = str(datetime.datetime.now(datetime.timezone.utc).timestamp()).replace('.', '-')
        target_file = f'cams_download_{timestamp}.grib'
        c.retrieve(
            'cams-global-reanalysis-eac4',
            {
                'variable': [
                    "2m_temperature",
                    "mean_sea_level_pressure",
                    "particulate_matter_2.5um",
                    "particulate_matter_10um",
                    "carbon_monoxide",
                    "nitrogen_dioxide",
                    "ozone",
                    "sulphur_dioxide"
                ],
                "model_level": ["60"],
                "date": [f"{self.start_date}/{self.end_date}"],
                'time': ['00:00', '03:00', '06:00', '09:00',
                         '12:00', '15:00', '18:00', '21:00'],
                'area': [max_lat, min_lon, min_lat, max_lon],
                'data_format': 'grib',
            },
            target_file)

        # GRIB_edition: 1/2
        edition_1 = xr.open_dataset(
            target_file,
            engine="cfgrib",
            decode_timedelta=False,
            backend_kwargs={"filter_by_keys": {"edition": 1}}).drop_vars(["number", "surface"],
                                                                         errors="ignore"
                                                                         )
        edition_2 = xr.open_dataset(
            target_file,
            engine="cfgrib",
            decode_timedelta=False,
            backend_kwargs={"filter_by_keys": {"edition": 2}}).drop_vars(["hybrid"],
                                                                         errors="ignore"
                                                                         )

        # assign coordinate with first dataarray to fix 1) use 360 degree system issue 2) slightly different lat lons
        edition_2 = edition_2.assign_coords(edition_1.coords)

        data = xr.merge([edition_1, edition_2])

        # unit conversion
        # particulate matter: concentration * 10^9
        # target unit is ug/m3
        for var in ['pm2p5', 'pm10']:
            data[var].values = data[var].values * (10 ** 9)
        # other: concentration x pressure / (287.058 * temp) * 10^9
        # target unit is ug/m3
        for var in ['co', 'no2', 'go3', 'so2']:
            data[var].values = data[var].values * data['msl'].values / \
                (287.058 * data['t2m'].values) * (10 ** 9)
        # drop pressure and temperature
        data = data.drop_vars(['msl', 't2m'])
        # xarray.Dataset to xarray.DataArray
        data = data.to_array()

        # Remove local files
        for file in glob.glob(f'{target_file}*'):
            os.remove(file)

        # Select the nearest data point based on latitude and longitude
        # center_lon = (min_lon + max_lon) / 2
        # center_lat = (min_lat + max_lat) / 2
        # data = data.sel(latitude=center_lat,
        #                 longitude=center_lon,
        #                 method="nearest")

        # Rename and set x, y as spatial dims
        data = data.rename({'longitude': 'x', 'latitude': 'y'})
        wgs_crs = bbox.as_geographic_bbox().crs
        data = data.rio.write_crs(wgs_crs)
        data.rio.set_spatial_dims(x_dim='x', y_dim='y', inplace=True)

        if self.species:
            data = data.sel(variable=[var.value['eac4_varname'] for var in self.species])

        return data
