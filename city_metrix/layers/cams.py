import cdsapi
import os
import xarray as xr
import zipfile

from .layer import Layer


class Cams(Layer):
    def __init__(self, start_date="2023-01-01", end_date="2023-12-01", species, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
		if species in ("particulate_matter_2.5um", "particulate_matter_10um", "carbon_monoxide", "nitrogen_dioxide", "ozone", "sulphur_dioxide"):
		    self.species = species
		else:
		    raise Exception("Selected species not supported")

    def get_data(self, bbox):
        min_lon, min_lat, max_lon, max_lat = bbox

        c = cdsapi.Client()
		query_dict = {
                "model_level": ["60"],
                "date": [f"{self.start_date}/{self.end_date}"],
                'time': ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
                'area': [max_lat, min_lon, min_lat, max_lon],
                'data_format': 'netcdf_zip',
            }
		if self.species in ("particulate_matter_2.5um", "particulate_matter_10um"):
		    query_dict['variable'] = [self.species]
		else:
		    query_dict['variable'] = [
			        "2m_temperature", "mean_sea_level_pressure", self.species
			    ]

        c.retrieve(
            'cams-global-reanalysis-eac4',
            query_dict,
            'cams_download.zip')

        # extract the ZIP file
        os.makedirs('cams_download', exist_ok=True)
        with zipfile.ZipFile('cams_download.zip', 'r') as zip_ref:
            # Extract all the contents of the ZIP file to the specified directory
            zip_ref.extractall('cams_download')

        # load netcdf files
        dataarray_list = []
        for nc_file in os.listdir('cams_download'):
            dataarray = xr.open_dataset(f'cams_download/{nc_file}')
            dataarray_list.append(dataarray)

        # not all variables have 'model_level', concatenate without 'model_level' dimension
        dataarray_list = [
            dataarray.squeeze(dim='model_level').drop_vars(['model_level'])
            if 'model_level' in dataarray.dims
            else dataarray
            for dataarray in dataarray_list
        ]

        # drop coordinate ['latitude','longitude'] if uses 360 degree system
        dataarray_list = [
            dataarray.drop_vars(['latitude', 'longitude'])
            if (dataarray['longitude'].values > 180).any()
            else dataarray
            for dataarray in dataarray_list
        ]
        data = xr.merge(dataarray_list)
        # xarray.Dataset to xarray.DataArray
        data = data.to_array()

        # Remove local files
        os.remove('cams_download.zip')
        for nc_file in os.listdir('cams_download'):
            os.remove(f'cams_download/{nc_file}')
        os.rmdir('cams_download')

        return data