import cdsapi
import os, datetime
import xarray as xr
import zipfile

from .layer import Layer


class Cams(Layer):
    def __init__(self, start_date="2023-01-01", end_date="2023-12-31", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def get_data(self, bbox):
        min_lon, min_lat, max_lon, max_lat = bbox

        c = cdsapi.Client()
        timestamp = str(datetime.datetime.utcnow().timestamp()).replace('.', '-')
        c.retrieve(
            'cams-global-reanalysis-eac4',
            {
                'variable': [
                    "2m_temperature", "mean_sea_level_pressure",
                    "particulate_matter_2.5um", "particulate_matter_10um",
                    "carbon_monoxide", "nitrogen_dioxide", "ozone", "sulphur_dioxide"
                ],
                "model_level": ["60"],
                "date": [f"{self.start_date}/{self.end_date}"],
                'time': ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
                'area': [max_lat, min_lon, min_lat, max_lon],
                'data_format': 'netcdf_zip',
            },
            f'cams_download_{timestamp}.zip')

        fname = f'cams_download_{timestamp}'
        os.makedirs(fname, exist_ok=True)

        # extract the ZIP file
        with zipfile.ZipFile(f'cams_download_{timestamp}.zip', 'r') as zip_ref:
            # Extract all the contents of the ZIP file to the specified directory
            zip_ref.extractall(fname)

        # load netcdf files
        dataarray_list = []
        for nc_file in os.listdir(fname):
            with xr.open_dataset(f'{fname}/{nc_file}') as dataarray:
                dataarray_list.append(dataarray)

        # not all variables have 'model_level', concatenate without 'model_level' dimension
        dataarray_list = [
            dataarray.squeeze(dim='model_level').drop_vars(['model_level'])
            if 'model_level' in dataarray.dims
            else dataarray
            for dataarray in dataarray_list
        ]
        # assign coordinate with last dataarray to fix 1) use 360 degree system issue 2) slightly different lat lons
        dataarray_list = [
            dataarray.assign_coords(dataarray_list[-1].coords)
            for dataarray in dataarray_list
        ]
        data = xr.merge(dataarray_list)

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
        os.remove(f'cams_download_{timestamp}.zip')
        # Workaround for elusive permission error
        try:  
            for nc_file in os.listdir(fname):
                os.remove(f'{fname}/{nc_file}')
            os.rmdir(fname)
        except:
            pass

        # Select the nearest data point based on latitude and longitude
        center_lon = (min_lon + max_lon) / 2
        center_lat = (min_lat + max_lat) / 2
        data = data.sel(latitude=center_lat, longitude=center_lon, method="nearest")

        return data
