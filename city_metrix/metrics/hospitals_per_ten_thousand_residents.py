import pandas as pd
from typing import Union
import datetime

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import GeoZone, GeoExtent, Metric
from city_metrix.layers import OpenStreetMap, OpenStreetMapClass, WorldPop


class HospitalsPerTenThousandResidents__Hospitals(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["year"]

    def __init__(self, year=datetime.datetime.now().year, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.unit = 'hospitals'

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:

        hospitals = OpenStreetMap(osm_class=OpenStreetMapClass.HOSPITAL).get_data(GeoExtent(geo_zone))
        hospital_counts_per_zone = geo_zone.zones.copy()
        hospital_counts_per_zone['value'] = [
                hospitals.geometry.intersects(zone).sum()
                for zone in geo_zone.zones.geometry
            ]

        world_pop = WorldPop()
        world_pop_sum = world_pop.groupby(geo_zone).sum()

        if isinstance(world_pop_sum, pd.DataFrame):
            result = world_pop_sum.copy()
            result['value'] = 10000 * hospital_counts_per_zone['value'] / world_pop_sum['value']

        else:
            result = 10000 * hospital_counts_per_zone / world_pop_sum

        return result
