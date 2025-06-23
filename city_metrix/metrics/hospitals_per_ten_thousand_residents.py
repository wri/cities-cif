from pandas import Series
from geopandas import GeoSeries

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import OpenStreetMap, OpenStreetMapClass, WorldPop
from city_metrix.metrix_model import GeoZone, Metric


class HospitalsPerTenThousandResidents(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:

        world_pop = WorldPop()
        hospitals = OpenStreetMap(osm_class=OpenStreetMapClass.HOSPITAL)

        hospital_count = hospitals.mask(world_pop).groupby(geo_zone).count()
        world_pop_sum = world_pop.groupby(geo_zone).sum()

        return 10000 * hospital_count.fillna(0) / world_pop_sum
