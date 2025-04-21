from geopandas import GeoDataFrame, GeoSeries
from city_metrix.layers import Layer, ImperviousSurface
from city_metrix.metrics.metric import Metric

class PercentAreaImpervious(Metric):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 zones: GeoDataFrame,
                 spatial_resolution:int = None) -> GeoSeries:
        imperv = ImperviousSurface()

        # monkey‐patch impervious get_data to fill na
        imperv_fillna = ImperviousSurface()
        imperv_fillna_get_data = imperv_fillna.get_data
        imperv_fillna.get_data = lambda bbox, spatial_resolution: imperv_fillna_get_data(bbox, spatial_resolution).fillna(0)

        # count with no NaNs
        imperv_count = imperv.groupby(zones).count()
        # count all pixels
        imperv_fillna_count = imperv_fillna.groupby(zones).count()

        return 100 * imperv_count / imperv_fillna_count
