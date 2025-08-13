import xarray as xr
import ee

from city_metrix.metrix_model import GeoExtent, Layer, get_image_collection
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 1113.1949  # 10 degrees of earth circumference


class CamsGhg(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["species"]
    MINOR_NAMING_ATTS = ["sector", "co2e"]

    # Returned units: metric tonnes of GHG species or tonnes CO2e
    SUPPORTED_SPECIES = {
        'co2': {'GWP': 1,  # by definition
                'sectors': ['ags', 'awb', 'ene', 'fef', 'ind', 'ref', 'res', 'shp', 'slv', 'sum', 'swd', 'tnr', 'tro']
                },
        'ch4': {'GWP': 28,  # https://www.ipcc.ch/site/assets/uploads/2018/02/WG1AR5_Chapter08_FINAL.pdf
                'sectors': ['agl', 'ags', 'awb', 'ene', 'fef', 'ind', 'ref', 'res', 'shp', 'sum', 'swd', 'tnr', 'tro']
                },
        'n2o': {'GWP': 265,  # https://www.ipcc.ch/site/assets/uploads/2018/02/WG1AR5_Chapter08_FINAL.pdf
                'sectors': ['ags', 'awb', 'ene', 'fef', 'ind', 'ref', 'res', 'slv', 'sum', 'swd', 'tnr', 'tro']
                },
        'chlorinated-hydrocarbons': {'GWP': 400,  # Table A2 https://onlinelibrary.wiley.com/doi/pdf/10.1002/0470865172.app2# 
                                     'sectors': ['ene', 'fef', 'ind', 'res', 'shp', 'slv', 'sum', 'tnr', 'tro']
                                     }
    }
    SUPPORTED_YEARS = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

    def __init__(self, species=None, sector='sum', co2e=True, year=2023, **kwargs):
        super().__init__(**kwargs)
        if species is not None and not species in self.SUPPORTED_SPECIES.keys():
            raise Exception(f'Unsupported species: {species}')
        if not year in self.SUPPORTED_YEARS:
            raise Exception(f'Unsupported year: {year}')
        if species is None and co2e == False:
            raise Exception('If sector is unspecified, all supported species will be summed and co2e must be True.')
        if species is None and sector != 'sum':
            raise Exception('If sector is unspecified, sector must be \"sum\".')
        if species is not None and sector != 'sum':
            if not sector in self.SUPPORTED_SPECIES[species]['sectors']:
                raise Exception(f'Sector \"{sector}\" not available for {species}.')

        self.species = species  # None means all, summed
        self.sector = sector
        self.co2e = co2e # Want results in CO2e? If so, multiplies by 100-year GWP.
        self.year = year  # Currently supported: 2010, 2015, 2020, 2023

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_cache_retrieval=False):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        
        ee_rectangle  = bbox.to_ee_rectangle()

        if self.species is not None:
            data_ic = ee.ImageCollection(f'projects/wri-datalab/cams-glob-ant/{self.species}_v6-2')
            data_im = data_ic.filter(ee.Filter.eq('year', self.year)).first().select(self.sector)
            if self.co2e:
                data_im = data_im.multiply(self.SUPPORTED_SPECIES[self.species]['GWP'])
            data_im = data_im.multiply(1000000)  # Tg to tonne
            cams_ghg_ic = ee.ImageCollection(data_im)

            data = get_image_collection(
                cams_ghg_ic,
                ee_rectangle,
                spatial_resolution,
                "CAMS GHG"
            )['self.species']

        else:  # Sum over all species
            allrasters_list = []
            for species in self.SUPPORTED_SPECIES.keys():
                data_ic = ee.ImageCollection(f'projects/wri-datalab/cams-glob-ant/{species}')
                data_im = data_ic.filter(ee.Filter.eq('year', self.year)).first().select('sum')
                data_im = data_im.multiply(self.SUPPORTED_SPECIES[species]['GWP'])
                data_im = data_im.multiply(1000000)  # Tg to tonne
                allrasters_list.append(data_im)
            allrasters_ic = ee.ImageCollection(allrasters_list)
            sum_im = allrasters_ic.sum()
            
            cams_ghg_ic = ee.ImageCollection(sum_im)

            data = get_image_collection(
                cams_ghg_ic,
                ee_rectangle,
                spatial_resolution,
                "CAMS GHG"
            )['sum']

        return data
