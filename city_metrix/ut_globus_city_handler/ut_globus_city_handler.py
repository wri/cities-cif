import os
import re
import geopandas as gpd


def search_for_ut_globus_city_by_contained_polygon(query_polygon, utm_crs):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    gpkg_path = os.path.join(script_dir, 'global_ut_globus_cities.gpkg')

    gdf = gpd.read_file(gpkg_path, layer='ut_globus_cities')
    gdf = gdf.to_crs(utm_crs)
    query_polygon = gpd.GeoSeries([query_polygon], crs=gdf.crs).to_crs(utm_crs).iloc[0]

    # Find the record with the greatest overlap
    gdf['overlap_area'] = gdf['geometry'].intersection(query_polygon).area
    max_overlap_record = gdf.loc[gdf['overlap_area'].idxmax()]

    if gdf["overlap_area"].max() <= 0:
        return None
    else:
        label = max_overlap_record['Label']
        # remove leading underscore and tif extension
        city_name = label.lstrip("_").rstrip(".tif").lower()
        # remove trailing number with undersore
        city_name = re.sub(r'_\d+$', '', city_name)
        return city_name

# Example run
# from shapely.geometry.polygon import Polygon
# from pyproj import CRS
# query_polygon_coordinates = Polygon([(-122.3355, 47.6079), (-122.3358, 47.6081), (-122.3353, 47.6083), (-122.3355, 47.6079)])
# utm_crs = CRS.from_epsg(32610)
# record = search_for_ut_globus_city_by_contained_polygon(query_polygon_coordinates)
# if record:
#     print("Matching record found:", record)
# else:
#     print("No matching record found.")
