from enum import Enum
import osmnx as ox
import geopandas as gpd
import pandas as pd

from .layer import Layer
from .layer_geometry import GeoExtent


class OpenStreetMapClass(Enum):
    # ALL includes all 29 primary features https://wiki.openstreetmap.org/wiki/Map_features
    ALL = {'aerialway': True, 'aeroway': True, 'amenity': True, 'barrier': True, 'boundary': True, 
           'building': True, 'craft': True, 'emergency': True, 'geological': True, 'healthcare': True,
           'highway': True, 'historic': True, 'landuse': True, 'leisure': True, 'man_made': True,
           'military': True, 'natural': True, 'office': True, 'place': True, 'power': True,
           'public_transport': True, 'railway': True, 'route': True, 'shop': True, 'sport': True,
           'telecom': True, 'tourism': True, 'water': True, 'waterway': True}
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
    """
    Attributes:
        osm_class: Enum value from OpenStreetMapClass
        buffer_distance: meters distance for buffer around osm features
    """

    def __init__(self, osm_class=OpenStreetMapClass.ALL, buffer_distance=None,**kwargs):
        super().__init__(**kwargs)
        self.osm_class = osm_class
        self.buffer_distance = buffer_distance  # meters

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None):
        #Note: spatial_resolution and resampling_method arguments are ignored.

        if bbox.units == "degrees":
            min_lon = bbox.min_x
            min_lat = bbox.min_y
            max_lon = bbox.max_x
            max_lat = bbox.max_y
            utm_crs = bbox.as_utm_bbox().crs
        else:
            wgs_bbox = bbox.as_geographic_bbox()
            min_lon = wgs_bbox.min_x
            min_lat = wgs_bbox.min_y
            max_lon = wgs_bbox.max_x
            max_lat = wgs_bbox.max_y
            utm_crs = bbox.crs

        # Set the OSMnx configuration to disable caching
        ox.settings.use_cache = False
        try:
            osm_feature = ox.features_from_bbox(bbox=(min_lon, min_lat, max_lon, max_lat), tags=self.osm_class.value)
        # When no feature in bbox, return an empty gdf
        except ox._errors.InsufficientResponseError as e:
            osm_feature = gpd.GeoDataFrame(pd.DataFrame(columns=['id', 'geometry']+list(self.osm_class.value.keys())), geometry='geometry')
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
        keep_col = ['id', 'geometry']
        for key in self.osm_class.value:
            if key in osm_feature.columns:
                keep_col.append(key)
        # keep 'lanes' for 'highway'
        if 'highway' in keep_col and 'lanes' in osm_feature.columns:
            keep_col.append('lanes')
        osm_feature = osm_feature.reset_index()[keep_col]

        osm_feature = osm_feature.to_crs(utm_crs)

        if self.buffer_distance:
            osm_feature['geometry'] = osm_feature.geometry.buffer(self.buffer_distance)

        return osm_feature
