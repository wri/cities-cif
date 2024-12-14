import xarray as xr
import ee

from .layer import Layer

class CamsGhg(Layer):
	# Returned units: metric tonnes of GHG species or tonnes CO2e
	
	GWP = {
		'co2': 1  # by definition
		'ch4': 28,  # https://www.ipcc.ch/site/assets/uploads/2018/02/WG1AR5_Chapter08_FINAL.pdf
		'chlorinated-hydrocarbons': 400,  # Table A2 https://onlinelibrary.wiley.com/doi/pdf/10.1002/0470865172.app2
		'n2o': 265  # https://www.ipcc.ch/site/assets/uploads/2018/02/WG1AR5_Chapter08_FINAL.pdf
	}
	SUPPORTED_SPECIES = ['co2', 'ch4', 'n2o', 'chlorinated-hydrocarbons']
	SUPPORTED_YEARS = [2010, 2015, 2020, 2023]

    def __init__(self, species=None, sector='sum', co2e=True, year=2023, **kwargs):
        super().__init__(**kwargs)
		if species is not None and not species in SUPPORTED_SPECIES:
			raise Except(f'Unsupported species: {species}')
		if not year in SUPPORTED_YEARS:
			raise Except(f'Unsupported year: {year}')
		if species is None and co2e==False:
			raise Except('If sector is unspecified, all supported species will be summed and co2e must be True.')
		if species is None and sector != 'sum':
			raise Except('If sector is unspecified, sector must be \"sum.\"')
		if species is not None and sector != 'sum':
			data_ic = ee.ImageCollection(f'projects/wri-datalab/cams-glob-ant/{species}').filter('year', year)
			sectors = data_ic.aggregate_array('sector').getInfo()
			if not sector in sectors:
				raise Except(f'Sector \"{sector}\" not available for {species} in {year}.')
		self.species = species  # None means all, summed
		self.sector = sector
		self.co2e = co2e  # Want results in CO2e? If so, multiplies by 100-year GWP.
		self.year = year  # Currently supported: 2010, 2015, 2020, 2023

     def get_data(self, bbox):
		if self.species is not None:
			data_ic = ee.ImageCollection(f'projects/wri-datalab/cams-glob-ant/{self.species}')
			data_im = data_ic.filter(ee.Filter.eq('year', self.year)).filter(ee.Filter.eq('sector', self.sector)).first()
			scale = data_im.projection().getInfo()['transform'][0]
			data_im = data_im.multiply(GWP[self.species])
			if self.co2e:
				data_im = data_im.multiply(GWP[self.species])
			data_im = data_im.multiply(1000000)  # Tg to tonne
			ic = ee.ImageCollection(data_im)
			scale = data_im.projection().getInfo()['transform'][0]
			ds = xr.open_dataset(
				ic,
				engine = 'ee',
				geometry = bbox,
				crs = 'EPSG:4326',
				scale = scale
			)
		else:  # Sum over all species
			allrasters_ic = ee.ImageCollection([])
			for species in SUPPORTED_SPECIES[1:]:
				data_ic = ee.ImageCollection(f'projects/wri-datalab/cams-glob-ant/{species}')
				data_im = data_ic.filter(ee.Filter.eq('year', self.year)).filter(ee.Filter.eq('sector', 'sum')).first()
				data_im = data_im.multiply(GWP[species])
				data_im = data_im.multiply(1000000)  # Tg to tonne
				allrasters_ic = summed_rasters.add(data_im)
			sum_im = allrasters_ic.sum()
			scale = sum_im.projection().getInfo()['transform'][0]
			ic = ee.ImageCollection(sum_im)
			ds = xr.open_dataset(
				ic,
				engine = 'ee',
				geometry = bbox,
				crs = 'EPSG:4326',
				scale = scale
			)
		ds = ds.transpose('time', 'lat', 'lon')
		ds = ds.squeeze()
		ds = ds.rio.set_spatial_dims('lon', 'lat')
		return ds
		