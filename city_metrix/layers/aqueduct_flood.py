from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_image_collection
from .layer_geometry import GeoExtent
from .layer_tools import build_s3_names

DEFAULT_SPATIAL_RESOLUTION = 100

class AqueductFlood(Layer):
    OUTPUT_FILE_FORMAT = 'tif'

    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
        return_period_c: default "rp0100"
                         options ["rp0002", "rp0005", "rp0010", "rp0025", "rp0050", "rp0100", "rp0250", "rp0500", "rp1000"]
                         note: return period 1.5 is only available for certain settings.
        return_period_r: default "rp00100"
                         options ["rp00002", "rp00005", "rp00010", "rp00025", "rp00050", "rp00100", "rp00250", "rp00500", "rp01000"]
                         note: return period 1.5 is only available for certain settings.
        end_year: default 2050
                  options [1980, 2030, 2050, 2080]
                  note: If 1980, may need to remove some filters that are not available as properties in those images.
        climate: default "rcp4p5"
                 options ["historical", "rcp4p5", "rcp8p5"]
        subsidence: default "nosub"
                    options ["nosub", "wtsub"]
        sea_level_rise_scenario: default 50
                                 options [5, 50]
    """

    def __init__(self, return_period_c="rp0100", return_period_r="rp00100", end_year=2050, climate="rcp4p5", subsidence='nosub', sea_level_rise_scenario=50, **kwargs):
        super().__init__(**kwargs)
        self.return_period_c = return_period_c
        self.return_period_r = return_period_r
        self.end_year = end_year
        self.climate = climate
        self.subsidence = subsidence
        self.sea_level_rise_scenario = sea_level_rise_scenario

    def get_layer_names(self):
        minor_qualifier = {"return_period_c": self.return_period_c,
                           "return_period_r": self.return_period_r,
                           "climate": self.climate,
                           "subsidence": self.subsidence,
                           "sea_level_rise_scenario": self.sea_level_rise_scenario}

        layer_name, layer_id, file_format = build_s3_names(self, minor_qualifier, minor_qualifier)
        return layer_name, layer_id, file_format

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_s3_cache_retrieval=False):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        # read Aqueduct Floods data
        flood_image = ee.ImageCollection("projects/WRI-Aquaduct/floods/Y2018M08D16_RH_Floods_Inundation_EE_V01/output_V06/inundation")

        def constYear(img):
            return ee.Image(
                ee.Algorithms.If(
                    img.get('year_string'),
                    img.set('year', 1980),
                    img
                )
            )

        flood_image = flood_image.map(constYear)

        # Shared flooding variables
        min_innundation = 0

        coastal_end = (flood_image.filterMetadata("floodtype", "equals", "inuncoast")
                       .filterMetadata("returnperiod", "equals", self.return_period_c)
                       .filterMetadata("year", "equals", self.end_year)
                       .filterMetadata("climate", "equals", self.climate)
                       .filterMetadata("subsidence", "equals", self.subsidence)
                       .filterMetadata("sea_level_rise_scenario", "equals", self.sea_level_rise_scenario)
                       .first()
                       )

        riverine_end = (flood_image.filterMetadata("floodtype", "equals", "inunriver")
                        .filterMetadata("returnperiod", "equals", self.return_period_r)
                        .filterMetadata("year", "equals", self.end_year)
                        .filterMetadata("climate", "equals", self.climate)
                        ).reduce(ee.Reducer.mean()).rename('b1')  # average of all 5 models

        combflood_end = coastal_end.max(riverine_end)
        combflood_end = combflood_end.updateMask(combflood_end.gt(min_innundation))

        ee_rectangle  = bbox.to_ee_rectangle()
        data = get_image_collection(
            ee.ImageCollection(combflood_end),
            ee_rectangle,
            spatial_resolution,
            "aqueduct flood"
        ).b1

        return data
