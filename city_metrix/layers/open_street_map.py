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
    COMMERCE = {'building': ['bank', 'commercial', 'office', 'pub', 'restaurant', 'retail', 'shop', 'store', 'supermarket'],
                'landuse': ['commercial', 'retail'],
                'amenity': ['animal_boarding', 'animal_shelter', 'bank', 'biergarten', 'cafe', 'casino', 'childcare', 'fast_food', 'food_court', 'mortuary', 'nightclub', 'restaurant', 'studio', 'theatre', 'veterinary']}
    HEALTHCARE_SOCIAL = {'building': ['clinic', 'hospital'],
                         'amenity': ['dentist', 'doctors', 'hospital', 'nursing_home', 'pharmacy', 'social_facility']}
    MEDICAL = {'building': ['clinic', 'hospital'],
               'amenity': ['doctors', 'hospital']}
    AGRICULTURE = {'building': ['poultry_house'],
                   'landuse': ['animal_keeping', 'aquaculture', 'farm', 'farmyard', 'greenhouse_horticulture', 'orchard', 'paddy', 'plant_nursury', 'vinyard'],
                   'amenity': ['animal_breeding']}
    GOVERNMENT = {'building': ['government', 'government_office'],
                  'amenity': ['courthouse', 'fire_station', 'library', 'police', 'post_office', 'townhall']}
    INDUSTRY = {'building': ['factory', 'industrial', 'manufacture'],
                'landuse': ['industrial', 'quarry'],
                'industrial': True}
    TRANSPORTATION_LOGISTICS = {'building': ['warehouse'],
                                'landuse': ['harbour'],
                                'amenity': ['bus_station', 'ferry_terminal'],
                                'railway': ['station'],
                                'aeroway': ['terminal'],
                                'industrial': ['port'],
                                'cargo': True}
    EDUCATION = {'building': ['college', 'school', 'university'],
                 'landuse': ['education'],
                 'amenity': ['college', 'kindergarten', 'music_school', 'prep_school', 'research_institute', 'school', 'university'],
                 'school': True}
    PRIMARY_SECONDARY_EDUCATION = {'building': ['school',],
                                   'amenity': ['school', 'kindergarten'],
                                   'school': True}
    HIGHER_EDUCATION = {'amenity': ['college', 'university', 'research_institute'],
                        'building': ['college', 'university']}
    TRANSIT_STOP = {'amenity': ['ferry_terminal'],
                    'railway': ['stop', 'platform', 'halt', 'tram_stop', 'subway_entrance', 'station'],
                    'highway': ['bus_stop', 'platform'],
                    'public_transport': ['platform', 'stop_position', 'stop_area'],
                    'station': ['subway'],
                    'aerialway': ['station']}


class OpenStreetMap(Layer):
    def __init__(self, osm_class=OpenStreetMapClass.ALL, **kwargs):
        super().__init__(**kwargs)
        self.osm_class = osm_class

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None):
        # Note: spatial_resolution and resampling_method arguments are ignored.

        min_lon, min_lat, max_lon, max_lat = bbox.as_geographic_bbox().bounds
        utm_crs = bbox.as_utm_bbox().crs

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
            # Filter out LineString
            osm_feature = osm_feature[osm_feature.geom_type.isin(['Point', 'Polygon', 'MultiPolygon'])]

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

        return osm_feature
