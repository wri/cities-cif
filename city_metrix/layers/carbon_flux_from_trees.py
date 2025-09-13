import ee

from city_metrix.metrix_model import Layer, get_image_collection, GeoExtent
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 30

class CarbonFluxFromTrees(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    """
    Average annual carbon emissions minus removal in tonnes CO2e over 21-yer period 2001-2021. Not a time series. Model 1.2.2.
    See Harris et al. 2021 Nature Climate Change (nature.com/articles/s41558-020-00976-6). Contacts: david.gibbs@wri.org and nharris@wri.org

    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        netflux_total_ic = ee.ImageCollection('projects/wri-datalab/gfw-data-lake/net-flux-forest-extent-per-ha-v1-2-2-2001-2021/net-flux-global-forest-extent-per-ha-2001-2021')
        netflux_total_img = netflux_total_ic.mosaic()
        netflux_annual_img = netflux_total_img.divide(21).divide(10000).multiply(spatial_resolution**2)  # Divide by 21 years, convert from per-hectare to per pixel-area

        ee_rectangle  = bbox.to_ee_rectangle()
        data = get_image_collection(
                ee.ImageCollection(netflux_annual_img),
                ee_rectangle,
                spatial_resolution,
                "tree carbon flux",
            ).b1.fillna(0)

        return data
