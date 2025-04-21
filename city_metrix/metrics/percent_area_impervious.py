from geopandas import GeoSeries

from city_metrix.constants import GEOJSON_FILE_EXTENSION
from city_metrix.layers import ImperviousSurface
from city_metrix.metrix_model import Metric, GeoZone


class PercentAreaImpervious(Metric):
    GEOSPATIAL_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:
        imperv = ImperviousSurface()

        # monkey‐patch impervious get_data to fill na
        imperv_fillna = ImperviousSurface()
        imperv_fillna_get_data = imperv_fillna.get_data
        imperv_fillna.get_data = lambda bbox, spatial_resolution: imperv_fillna_get_data(bbox, spatial_resolution).fillna(0)

        # count with no NaNs
        imperv_count = imperv.groupby(geo_zone).count()
        # count all pixels
        imperv_fillna_count = imperv_fillna.groupby(geo_zone).count()

        return 100 * imperv_count / imperv_fillna_count
