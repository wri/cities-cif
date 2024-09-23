from enum import Enum
import osmnx as ox
import geopandas as gpd
import pandas as pd

from .layer import Layer
from .layer import get_utm_zone_epsg


class OpenStreetMapClass(Enum):
    OPEN_SPACE = {'leisure': ['park', 'nature_reserve', 'common', 'playground', 'pitch', 'track'],
                  'boundary': ['protected_area', 'national_park']}
    OPEN_SPACE_HEAT = {'leisure': ['park', 'nature_reserve', 'common', 'playground', 'pitch', 'garden', 'golf_course', 'dog_park', 'recreation_ground', 'disc_golf_course'],
                       'boundary': ['protected_area', 'national_park', 'forest_compartment', 'forest']}
    WATER = {'water': True,
             'natural': ['water'],
             'waterway': True}
    ROAD = {'highway': ["residential", "service", "unclassified", "tertiary", "secondary", "primary", "turning_circle", "living_street", "trunk", "motorway", "motorway_link", "trunk_link",
                         "primary_link", "secondary_link", "tertiary_link", "motorway_junction", "turning_loop", "road", "mini_roundabout", "passing_place", "busway"]}
    BUILDING = {'building': True}
    PARKING = {'amenity': ['parking'],
               'parking': True}
    ECONOMIC_OPPORTUNITY = {'landuse': ['commercial', 'industrial', 'retail', 'institutional', 'education'],
							'building': ['office', 'commercial', 'industrial', 'retail', 'supermarket'],
							'shop': True}
    SCHOOLS = {'building': ['school',],
				'amenity': ['school', 'kindergarten']}
    HIGHER_EDUCATION = {'amenity': ['college', 'university'],
						'building': ['college', 'university']}
    TRANSIT_STOP = {'amenity':['ferry_terminal'],
                    'railway':['stop', 'platform', 'halt', 'tram_stop', 'subway_entrance', 'station'],
                    'highway':['bus_stop', 'platform'],
                    'public_transport': ['platform', 'stop_position', 'stop_area'],
                    'station':['subway'],
                    'aerialway':['station']}


class OpenStreetMap(Layer):
    def __init__(self, osm_class=None, buffer_distance=None, **kwargs):
        super().__init__(**kwargs)
        self.osm_class = osm_class
        self.buffer_distance = buffer_distance  # meters

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

        # Filter by geo_type
        if self.osm_class == OpenStreetMapClass.ROAD:
            # Filter out Point
            osm_feature = osm_feature[osm_feature.geom_type != 'Point']
        elif self.osm_class == OpenStreetMapClass.TRANSIT_STOP:
            # Keep Point
            osm_feature = osm_feature[osm_feature.geom_type == 'Point']
        else:
            # Filter out Point and LineString
            osm_feature = osm_feature[osm_feature.geom_type.isin(['Polygon', 'MultiPolygon'])]

        # keep only columns desired to reduce file size
        keep_col = ['osmid', 'geometry']
        for key in self.osm_class.value:
            if key in osm_feature.columns:
                keep_col.append(key)
        # keep 'lanes' for 'highway'
        if 'highway' in keep_col and 'lanes' in osm_feature.columns:
            keep_col.append('lanes')
        osm_feature = osm_feature.reset_index()[keep_col]

        if self.buffer_distance is not None:
            target_crs = get_utm_zone_epsg(bbox)
            osm_feature_utm = osm_feature.to_crs(target_crs)
            osm_feature_utm_buffered = osm_feature_utm.buffer(self.buffer_distance)
            osm_feature = osm_feature_utm_buffered.to_crs("EPSG:4326")

        return osm_feature
