import cdsapi
import os
import xarray as xr
import glob

from .layer import Layer
from .layer_geometry import GeoExtent


class Cams(Layer):
    def __init__(self, start_date="2023-01-01", end_date="2023-12-31", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None):
        #Note: spatial_resolution and resampling_method arguments are ignored.

        if bbox.projection_name == 'geographic':
            min_lon = bbox.min_x
            min_lat = bbox.min_y
            max_lon = bbox.max_x
            max_lat = bbox.max_y
        else:
            wgs_bbox = bbox.as_geographic_bbox()
            min_lon = wgs_bbox.min_x
            min_lat = wgs_bbox.min_y
            max_lon = wgs_bbox.max_x
            max_lat = wgs_bbox.max_y

        c = cdsapi.Client(url='https://ads.atmosphere.copernicus.eu/api')
        target_file = 'cams_download.grib'
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
            backend_kwargs={"filter_by_keys": {"edition": 1}}).drop_vars(["number", "surface"], 
            errors="ignore"
            )
        edition_2 = xr.open_dataset(
            target_file, 
            engine="cfgrib", 
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
            data[var].values = data[var].values * data['msl'].values / (287.058 * data['t2m'].values) * (10 ** 9)

        # drop pressure and temperature
        data = data.drop_vars(['msl', 't2m'])
        # xarray.Dataset to xarray.DataArray
        data = data.to_array()

        # Remove local files
        for file in glob.glob(f'cams_download.grib*'):
            os.remove(file)

        # Select the nearest data point based on latitude and longitude
        center_lon = (min_lon + max_lon) / 2
        center_lat = (min_lat + max_lat) / 2
        data = data.sel(latitude=center_lat,
                        longitude=center_lon, 
                        method="nearest")

        return data
