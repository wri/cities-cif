from geopandas import GeoSeries

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import CarbonFluxFromTrees
from city_metrix.metrix_model import GeoZone, Metric

"""
Flux is emissions minus removal, in tonnes
See Harris et al. 2021 Nature Climate Change (nature.com/articles/s41558-020-00976-6). Contacts: david.gibbs@wri.org and nharris@wri.org

"""

class TreeCarbonFlux(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,  **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:

        flux = CarbonFluxFromTrees().groupby(geo_zone).sum()

        return flux
