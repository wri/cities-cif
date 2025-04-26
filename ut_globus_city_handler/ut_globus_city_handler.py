import os
import geopandas as gpd

def search_for_ut_globus_city_by_contained_polygon(query_polygon):
    dir_path = os.path.dirname(os.path.abspath(__file__))
    gpkg_path = os.path.join(dir_path, 'global_ut_globus_cities.gpkg')

    gdf = gpd.read_file(gpkg_path, layer='ut_globus_cities')
    containing_records = gdf[gdf.geometry.contains(query_polygon)]

    if containing_records is None:
        return None
    else:
        label = containing_records.iloc[0]['Label']
        city_name = label.lstrip("_").rstrip(".tif").lower()
        return city_name

# # # Example run
# from shapely.geometry.polygon import Polygon
# query_polygon_coordinates = Polygon([(-122.3355, 47.6079), (-122.3358, 47.6081), (-122.3353, 47.6083), (-122.3355, 47.6079)])
# record = search_for_ut_globus_city_by_contained_polygon(query_polygon_coordinates)
# if record:
#     print("Matching record found:", record)
# else:
#     print("No matching record found.")