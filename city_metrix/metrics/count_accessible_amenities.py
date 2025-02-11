from geopandas import GeoDataFrame, GeoSeries
from pandas import Series
from city_metrix.layers import Layer
from math import floor
import shapely

from city_metrix.layers import Isoline, UrbanLandUse, WorldPop
from city_metrix.layers.layer import get_utm_zone_epsg


def count_accessible_amenities(zones: GeoDataFrame, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, weighting='population', worldpop_agesex_classes=[], worldpop_year=2020, informal_only=False) -> GeoSeries:
    # cityname example: ARG-Buenos_Aires
    # amenityname is OSMclass names, in lowercase
    # travelmode is walk, bike, automobile, publictransit (only walk implemented for now)
    # threshold_value is integer, in minutes or meters
    # threshold_unit is usually minutes or meters

    class AccessCountTmp(Layer):
        def __init__(self, access_gdf, return_value, **kwargs):
            super().__init__(**kwargs)
            self.gdf = access_gdf[access_gdf['count_amenities']==return_value]
        def get_data(self, bbox):
            return self.gdf.clip(shapely.box(*bbox))

    class IsolinesBuffered(Isoline):
    # Stores and returns isochrone or isodistance polygons with polygons slightly buffered and simplified to avoid invalid-geometry errors
        def __init__(self, filename, **kwargs):
            super().__init__(filename=filename)
            iso_gdf = self.gdf
            if iso_gdf.crs in ('EPSG:4326', 'epsg:4326'):
                utm_epsg = get_utm_zone_epsg(iso_gdf.total_bounds)
                iso_gdf = iso_gdf.to_crs(utm_epsg).set_crs(utm_epsg)
            poly_list = [shapely.simplify(p.buffer(0.1), tolerance=10) for p in iso_gdf.geometry]  # Buffer and simplify
            buffered_gdf = GeoDataFrame({'accessible': 1, 'geometry': poly_list}).set_crs(utm_epsg)
            self.gdf = buffered_gdf.to_crs('EPSG:4326').set_crs('EPSG:4326')
            
        def get_data(self, bbox):
            return self.gdf.clip(shapely.box(*bbox))

    filename = f"{city_name}-{amenity_name}-{travel_mode}-{threshold_value}-{threshold_unit}-{retrieval_date}.geojson"

    population_layer = WorldPop(agesex_classes=worldpop_agesex_classes, year=worldpop_year)
    if informal_only:
        informal_layer = UrbanLandUse(return_value=3)
        population_layer.masks.append(informal_layer)

    iso_layer = IsolinesBuffered(filename=filename)
    results = []
    zones = zones.reset_index()
    for rownum in range(len(zones)):
        zone = zones.iloc[[rownum]]
        print('\n{0} (geo {1} of {2})'.format(zone.geo_name[rownum], rownum+1, len(zones)))
        iso_gdf = iso_layer.get_data(zone.total_bounds)
        if len(iso_gdf) == 0:
            results.append(0)
        else:
            if len(iso_gdf) == 1 and type(iso_gdf.iloc[0].geometry) == shapely.geometry.polygon.Polygon: # only one simple-polygon isoline
                dissected_gdf = GeoDataFrame({'poly_id': [0], 'geometry': [iso_gdf.iloc[0].geometry]}).set_crs('EPSG:4326')
            else:
                # Collect individual boundary linestrings of each isoline polygon
                iso_eachboundary = [iso_gdf.iloc[rownum]['geometry'].boundary for rownum in range(len(iso_gdf))]
                iso_boundarylinesmulti = [i for i in iso_eachboundary if i is not None]
                iso_boundarylines = []
                for i in iso_boundarylinesmulti:
                    if type(i) == shapely.geometry.linestring.LineString:
                        iso_boundarylines.append(i)
                    else:
                        for j in list(i.geoms):
                            iso_boundarylines.append(j)
                iso_bl_gdf = GeoDataFrame({'idx': range(len(iso_boundarylines)), 'geometry': iso_boundarylines})
                print("Converted isoline polygons into boundary multilines")
                # Dissolve all linestrings into large multilinestring, and polygonize into "dissected polygons"

                iso_dissected_polys = shapely.polygonize(list(iso_bl_gdf.dissolve().geometry[0].geoms))
                print("Creating gdf of dissected polygons")
                dissected_gdf = GeoDataFrame({'poly_id': range(len(list(iso_dissected_polys.geoms))), 'geometry': list(iso_dissected_polys.geoms)}).set_crs('EPSG:4326')
            # For each dissected polygon, find how many of the original isoline polys contain the centroid
            # This is the number of amenity points are accessible within the dissected polygon
            print("Counting original isoline polygons that intersect with each dissected polygon")
            count_amenities = dissected_gdf.centroid.within(iso_gdf.iloc[[0]].geometry[iso_gdf.index[0]]) * 1  # This is a Series storing running sum, a vector with num rows == num of dissected polys
            print("|==" + "PROGRESS=OF=INCLUSION=TESTS" + ("=" * 71) + "|")
            print(" ", end="")
            progress = 0

            for iso_idx in range(1, len(iso_gdf)):  # Iterate through all original isoline polys: test dissected polys to see whether centroids are included in isoline poly, add to running sum Series
                if floor(100 * iso_idx / len(iso_gdf)) > progress:
                    progress = floor(100 * iso_idx / len(iso_gdf))
                    print("X", end="")
                count_amenities = count_amenities + (dissected_gdf.centroid.within(iso_gdf.iloc[[iso_idx]].geometry[iso_gdf.index[iso_idx]]) * 1)
            print("X")
            dissected_gdf['count_amenities'] = count_amenities

            # Create dict of polygons each with a single asset-count
            max_count = dissected_gdf['count_amenities'].max()
            count_layers = {count: AccessCountTmp(access_gdf=dissected_gdf, return_value=count) for count in range(1, max_count + 1)}

            # For each zone, find average number of accessible amenities, and store in result_gdf

            running_sum = Series([0])
            for count in range(1, max_count+1):
                try: # Because adding masks to pop_layer adds them to WorldPop(), and they cannot be removed from WorldPop()
                    pop_layer
                except NameError:
                    pop_layer = WorldPop(agesex_classes=worldpop_agesex_classes, year=worldpop_year)
                else:
                    pop_layer.masks = []
                try:
                    totalpop_layer
                except NameError:
                    totalpop_layer = WorldPop(agesex_classes=worldpop_agesex_classes, year=worldpop_year)
                else:
                    totalpop_layer.masks = []
                if informal_only:
                    pop_layer.masks.append(informal_layer)
                    totalpop_layer.masks.append(informal_layer)
                pop_layer.masks.append(count_layers[count])
                groupby = pop_layer.groupby(zone)
                if weighting == 'area':
                    try:
                        running_sum += count * groupby.count().fillna(0)
                    except:
                        running_sum += Series([0])
                else: # weighting == 'population'
                    try:
                        running_sum += count * groupby.sum().fillna(0)
                    except:
                        running_sum += Series([0])
            if weighting == 'area':
                rowresult = running_sum / totalpop_layer.groupby(zone).count()
            else: # weighting == 'population'
                rowresult = running_sum / totalpop_layer.groupby(zone).sum()

            results.append(rowresult[0])

    result = Series(results)
    return result

def count_accessible_amenities_all(zones: GeoDataFrame, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, worldpop_year=2020) -> GeoSeries:
    agesex_classes = []
    return count_accessible_amenities(zones, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, "population", agesex_classes, worldpop_year, False)

def count_accessible_amenities_elderly(zones: GeoDataFrame, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, worldpop_year=2020) -> GeoSeries:
    agesex_classes = ['F_{0}'.format(i) for i in range(60, 85, 5)] + ['M_{0}'.format(i) for i in range(60, 85, 5)]
    return count_accessible_amenities(zones, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, "population", agesex_classes, worldpop_year, False)

def count_accessible_amenities_children(zones: GeoDataFrame, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, worldpop_year=2020) -> GeoSeries:
    agesex_classes = ['F_{0}'.format(i) for i in ['0', '1'] + list(range(5, 15, 5))] + ['M_{0}'.format(i) for i in ['0', '1'] + list(range(5, 15, 5))]
    return count_accessible_amenities(zones, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, "population", agesex_classes, worldpop_year, False)

def count_accessible_amenities_female(zones: GeoDataFrame, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, worldpop_year=2020) -> GeoSeries:
    agesex_classes = ['F_{0}'.format(i) for i in ['0', '1'] + list(range(5, 85, 5))]
    return count_accessible_amenities(zones, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, "population", agesex_classes, worldpop_year, False)

def count_accessible_amenities_informal(zones: GeoDataFrame, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, worldpop_year=2020) -> GeoSeries:
    agesex_classes = []
    return count_accessible_amenities(zones, city_name, amenity_name, travel_mode, threshold_value, threshold_unit, retrieval_date, "population", agesex_classes, worldpop_year, True)