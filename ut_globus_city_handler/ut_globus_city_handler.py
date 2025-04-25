import os.path

import fiona
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon


def search_for_ut_globus_city_by_contained_polygon(query_polygon):
    root_path = _get_project_root()
    gpkg_path = os.path.join(root_path, 'ut_globus_city_handler', 'global_ut_globus_cities.gpkg')

    # Open the specified layer in the GeoPackage
    feature_rec = None
    with fiona.open(gpkg_path, layer='ut_globus_cities') as layer:
        for feature in layer:
            polygon = shape(feature['geometry'])  # Convert the geometry to a Shapely object
            if polygon.contains(query_polygon):
                feature_rec = feature
                break

    if feature_rec is None:
        return None
    else:
        label = feature_rec['properties']['Label']
        city_name = label.lstrip("_").rstrip(".tif").lower()
        return city_name

def _get_project_root():
    from pathlib import Path

    # Start from the current file and search for the project root
    project_folder = Path(__file__).resolve().parent
    while not (project_folder / "environment.yml").exists() and project_folder != project_folder.parent:
        project_folder = project_folder.parent

    return project_folder

# Example run
# query_polygon_coordinates = Polygon([(-122.3355, 47.6079), (-122.3358, 47.6081), (-122.3353, 47.6083), (-122.3355, 47.6079)])
#
# record = search_for_ut_globus_city_by_contained_polygon(query_polygon_coordinates)
# if record:
#     print("Matching record found:", record)
# else:
#     print("No matching record found.")