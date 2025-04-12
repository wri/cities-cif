from geopandas import GeoDataFrame, GeoSeries
from pandas import Series
import ee
from city_metrix.layers import Layer, ProtectedAreas, EsaWorldCover
from city_metrix.layers.layer import get_image_collection
from city_metrix.metrics import GeoZone
from city_metrix.metrics.metric import Metric


class PercentProtectedArea(Metric):
    def __init__(self,
                 status=['Inscribed', 'Adopted', 'Designated', 'Established'],
                 status_year=2024,
                 iucn_cat=['Ia', 'Ib', 'II', 'III', 'IV', 'V', 'VI', 'Not Applicable', 'Not Assigned', 'Not Reported'],
                 **kwargs):
        super().__init__(**kwargs)
        self.status = status
        self.status_year = status_year
        self.iucn_cat = iucn_cat

    def get_data(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:

        world_cover = EsaWorldCover(year=2021)
        protect_area = ProtectedAreas(status=self.status, status_year=self.status_year, iucn_cat=self.iucn_cat)

        protect_area_in_world_cover = world_cover.mask(protect_area).groupby(geo_zone).count()
        world_cover_counts = world_cover.groupby(geo_zone).count()

        return 100 * protect_area_in_world_cover.fillna(0) / world_cover_counts
