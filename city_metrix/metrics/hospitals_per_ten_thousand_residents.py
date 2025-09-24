import pandas as pd
from typing import Union
import datetime
from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import GeoZone, Metric
from city_metrix.layers import OpenStreetMap, OpenStreetMapClass, WorldPop


class HospitalsPerTenThousandResidents__Hospitals(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self, year=datetime.datetime.now().year, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.unit = 'hospitals'

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> Union[pd.DataFrame | pd.Series]:

        world_pop = WorldPop()
        hospitals = OpenStreetMap(osm_class=OpenStreetMapClass.HOSPITAL)

        hospital_count = hospitals.mask(world_pop).groupby(geo_zone).count()
        world_pop_sum = world_pop.groupby(geo_zone).sum()

        if not isinstance(hospital_count, (int, float)):
            hospital_count = hospital_count.fillna(0)

        if isinstance(hospital_count, pd.DataFrame):
            result = hospital_count.copy()
            result['value'] = 10000 * (hospital_count['value'] / world_pop_sum['value'])
        else:
            result = 10000 * hospital_count / world_pop_sum

        return result
