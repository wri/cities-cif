from geopandas import GeoDataFrame, GeoSeries
from pandas import Series
import shapely

from city_metrix.layers.isoline import Isoline
from city_metrix.layers.world_pop import WorldPop
from city_metrix.layers.urban_land_use import UrbanLandUse
from city_metrix.layers.layer import Layer, get_utm_zone_epsg


def percent_population_access(zones, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, worldpop_agesex_classes=[], worldpop_year=2020, informal_only=False):
    # Example: city_name='MEX-Mexico_City', amenity_name='schools', travel_mode='walk', threshold_value=30, threshold_unit='minutes', retrieval_date='20241105'

    class IsolineSimplified(Isoline):
    # Stores and returns isochrone or isodistance polygons with simplified geometry, and dissolved into fewer non-overlapping polygons
        def __init__(self, filename, **kwargs):
            super().__init__(filename=filename)
            iso_gdf = self.gdf
            if iso_gdf.crs in ('EPSG:4326', 'epsg:4326'):
                utm_epsg = get_utm_zone_epsg(iso_gdf.total_bounds)
                iso_gdf = iso_gdf.to_crs(utm_epsg).set_crs(utm_epsg)
            poly_list = [shapely.simplify(p.buffer(0.1), tolerance=10) for p in iso_gdf.geometry]  # Buffer and simplify
            uu = shapely.unary_union(shapely.MultiPolygon(poly_list))  # Dissolve
            shorter_gdf = GeoDataFrame({'accessible': 1, 'geometry': list(uu.geoms)}).set_crs(utm_epsg)
            self.gdf = shorter_gdf.to_crs('EPSG:4326').set_crs('EPSG:4326')
            
        def get_data(self, bbox):
            return self.gdf.clip(shapely.box(*bbox))
    filename = f"{city_name}-{amenity_name}-{travel_mode}-{threshold_value}-{threshold_unit}-{retrieval_date}.geojson"
    iso_layer = IsolineSimplified(filename)
    accesspop_layer = WorldPop(agesex_classes=worldpop_agesex_classes, year=worldpop_year, masks=[iso_layer,])
    totalpop_layer = WorldPop(agesex_classes=worldpop_agesex_classes, year=worldpop_year)
    if informal_only:
        informal_layer = UrbanLandUse(return_value=3)
        accesspop_layer.masks.append(informal_layer)
        totalpop_layer.masks.append(informal_layer)
    res = []
    zones_reset = zones.reset_index()
    for rownum in range(len(zones_reset)):  # Doing it district-by-district to avoid empty-GDF error
        try:
            res.append(100 * accesspop_layer.groupby(zones_reset.iloc[[rownum]]).sum()[0] / totalpop_layer.groupby(zones_reset.iloc[[rownum]]).sum()[0])
        except:
            res.append(0)
    result = Series(res)
    return result

def percent_population_access_all(zones, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, worldpop_year=2020):
    agesex_classes = []
    return percent_population_access(zones, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, agesex_classes, worldpop_year, False)

def percent_population_access_children(zones, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, worldpop_year=2020):
    agesex_classes = ['F_{0}'.format(i) for i in ['0', '1'] + list(range(5, 15, 5))] + ['M_{0}'.format(i) for i in ['0', '1'] + list(range(5, 15, 5))]
    return percent_population_access(zones, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, agesex_classes, worldpop_year, False)

def percent_population_access_elderly(zones, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, worldpop_year=2020):
    agesex_classes = ['F_{0}'.format(i) for i in range(60, 85, 5)] + ['M_{0}'.format(i) for i in range(60, 85, 5)]
    return percent_population_access(zones, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, agesex_classes, worldpop_year, False)

def percent_population_access_female(zones, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, worldpop_year=2020):
    agesex_classes = ['F_{0}'.format(i) for i in ['0', '1'] + list(range(5, 85, 5))]
    return percent_population_access(zones, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, agesex_classes, worldpop_year, False)

def percent_population_access_informal(zones, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, worldpop_year=2020):
    agesex_classes = []
    return percent_population_access(zones, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, agesex_classes, worldpop_year, True)