from geopandas import GeoDataFrame, GeoSeries
import numpy as np

from city_metrix.layers.isoline import Isoline
from city_metrix.layers.world_pop import WorldPop

def count_accessible_amenities(zones: GeoDataFrame, cityname, amenityname, travelmode, threshold_type, threshold_value, isoline_year=2024, agesex_classes=[], worldpop_year=2020, aws_profilename=None) -> GeoSeries:
    
    class AccessCountTmp(Layer):
        def __init__(self, access_gdf, **kwargs):
            super().__init__(**kwargs)
            self.gdf = access_gdf
        def get_data(self, bbox):
            return self.gdf.clip(shapely.box(*bbox))
            
    def get_accessible_population(access_features_layer, popraster_layer, zones):

    # cityname example: ARG-Buenos-Aires
    # amenityname is OSMclass names, in lowercase
    # travelmode is walk, bike, automobile, publictransit (only walk implemented for now)
    # threshold_type is distance or time
    # threshold_value is integer, in minutes or meters
        population_layer = WorldPop(agesex_classes=agesex_classes, year=worldpop_year)
        params = {
            'cityname': cityname,
            'amenityname': amenityname,
            'travelmode': travelmode,
            'threshold_type': threshold_type,
            'threshold_value': threshold_value,
            'year': isoline_year
        }
        iso_layer = Isoline(params, aws_profilename=aws_profilename)
        iso_gdf = accesszone_layer.get_data(zones.total_bounds)
        
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
        iso_bl_gdf = gpd.GeoDataFrame({'idx': range(len(iso_boundarylines)), 'geometry': iso_boundarylines})
        
        # Dissolve all linestrings into large multilinestring, and polygonize into "dissected polygons"
        iso_dissected_polys = shapely.polygonize(list(iso_bl_gdf.dissolve().geometry[0].geoms))
        accesscount_gdf = gpd.GeoDataFrame({'poly_id': range(len(list(iso_dissected_polys.geoms))), 'geometry': list(iso_dissected_polys.geoms)})
        
        # For each dissected polygon, find how many of the original isoline polys contain the centroid
        # This is the number of amenity points are accessible within the dissected polygon
        count_amenities = iso_dissected_polys.centroid.within(iso_gdf.iloc[[0]].geometry[iso_gdf.index[0]]) * 1
        for iso_idx in range(1, len(iso_gdf)):
            count_amenities = count_amenities + (iso_dissected_polys.centroid.within(iso_gdf.iloc[[iso_idx]].geometry[iso_gdf.index[iso_idx]]) * 1)
            
        accesscount_gdf['count_amenities'] = count_amenities
        
        count_layers = {count: AccessCountTmp(gpd.GeoDataFrame({'count_amenities': polys_gdf['count_amenities']==count, 'geometry': polys_gdf['geometry']})) for count in range(1, polys_gdf['count_amenities'].max() + 1)}
        
        # For each zone, find average number of accessible amenities, and store in result_gdf
        max_count = polys_gdf['count_amenities'].max()
        result = population_layer.mask(count_layers[1]).count() / max_count
        for count in range(1, max_count+1):
            result += population_layer.mask(count_layers[count]).count() / max_count

        result_gdf['count_accessible_amenities'] = result
            
        return result_gdf