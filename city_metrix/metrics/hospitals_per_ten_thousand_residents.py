from pandas import Series
from geopandas import GeoSeries

from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.layers import OpenStreetMap, OpenStreetMapClass, WorldPop
from city_metrix.metrix_model import GeoExtent, GeoZone, Metric


class HospitalsPerTenThousandResidents(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    def __init__(self,
                 **kwargs):
        super().__init__(**kwargs)


    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution:int = None) -> GeoSeries:

        

        hospitals = OpenStreetMap(OpenStreetMapClass.HOSPITAL).get_data(GeoExtent(geo_zone))
        hospital_count = []
        for rownum in range(len(geo_zone.zones)):
            zone = geo_zone.zones.iloc[[rownum]]
            hospital_count.append(len(hospitals.loc[hospitals.to_crs('EPSG:4326').intersects(zone.geometry[rownum])]))
        hospital_count_series = Series(hospital_count)

        worldpop_layer = WorldPop(agesex_classes=[])
        return 10000 * hospital_count_series / worldpop_layer.groupby(geo_zone).sum()
        