from enum import Enum
import osmnx as ox
import geopandas as gpd
import pandas as pd

from .layer import Layer


class OpenStreetMapClass(Enum):
    OPEN_SPACE = {'leisure': ['park', 'nature_reserve', 'common', 'playground', 'pitch', 'track'],
                  'boundary': ['protected_area', 'national_park']}
    OPEN_SPACE_HEAT = {'leisure': ['park', 'nature_reserve', 'common', 'playground', 'pitch', 'track', 'garden', 'golf_course', 'dog_park', 'recreation_ground', 'disc_golf_course'],
                       'boundary': ['protected_area', 'national_park', 'forest_compartment', 'forest']}
    WATER = {'water': True,
             'natural': ['water'],
             'waterway': True}
    ROAD = {'highway': ["residential", "service", "unclassified", "tertiary", "secondary", "primary", "turning_circle", "living_street", "trunk", "motorway", "motorway_link", "trunk_link",
                         "primary_link", "secondary_link", "tertiary_link", "motorway_junction", "turning_loop", "road", "mini_roundabout", "passing_place", "busway"]}
    BUILDING = {'building': True}
    PARKING = {'amenity': ['parking'],
               'parking': True}


class OpenStreetMap(Layer):
    def __init__(self, osm_class=None, **kwargs):
        super().__init__(**kwargs)
        self.osm_class = osm_class

    def get_data(self, bbox):
        north, south, east, west = bbox[3], bbox[1], bbox[0], bbox[2]
        # Set the OSMnx configuration to disable caching
        ox.settings.use_cache = False
        try:
            osm_feature = ox.features_from_bbox(bbox=(north, south, east, west), tags=self.osm_class.value)
        # When no feature in bbox, return an empty gdf
        except ox._errors.InsufficientResponseError as e:
            osm_feature = gpd.GeoDataFrame(pd.DataFrame(columns=['osmid', 'geometry']+list(self.osm_class.value.keys())), geometry='geometry')
            osm_feature.crs = "EPSG:4326"

        # Filter out Point and LineString (if the feature is not ROAD)
        if self.osm_class != OpenStreetMapClass.ROAD:
            osm_feature = osm_feature[osm_feature.geom_type.isin(['Polygon', 'MultiPolygon'])]
        else:
            osm_feature = osm_feature[osm_feature.geom_type != 'Point']

        # keep only columns desired to reduce file size
        keep_col = ['osmid', 'geometry']
        for key in self.osm_class.value:
            if key in osm_feature.columns:
                keep_col.append(key)
        # keep 'lanes' for 'highway'
        if 'highway' in keep_col and 'lanes' in osm_feature.columns:
            keep_col.append('lanes')
        osm_feature = osm_feature.reset_index()[keep_col]

        return osm_feature

    def write(self, output_path):
        self.data['bbox'] = str(self.data.total_bounds)
        self.data['osm_class'] = str(self.osm_class.value)

        # Write to a GeoJSON file
        self.data.to_file(output_path, driver='GeoJSON')
