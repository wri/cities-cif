import ee
import geemap
import osmnx as ox
import geopandas as gpd
import pandas as pd
from enum import Enum

from city_metrix.constants import WGS_CRS, GEOJSON_FILE_EXTENSION, GTIFF_FILE_EXTENSION
from city_metrix.metrix_model import Layer, GeoExtent, get_image_collection

DEFAULT_SPATIAL_RESOLUTION = 100


def _merge_osm_classes(class_list):
    result = {}
    keys = {key for class_item in class_list for key in class_item}

    for key in keys:
        values = []
        for class_item in class_list:
            value = class_item.get(key)
            if value is True:
                values.append(True)
            elif value:
                values.extend(value)
        result[key] = True if True in values else list(set(values))

    return result


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
    HOSPITAL = {'building': ['hospital'],
                'amenity': ['hospital']}
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
    ECONOMIC = _merge_osm_classes(
        [COMMERCE, HEALTHCARE_SOCIAL, AGRICULTURE, GOVERNMENT, INDUSTRY, TRANSPORTATION_LOGISTICS, EDUCATION])


class OpenStreetMap(Layer):
    OUTPUT_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["osm_class"]
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        osm_class: OSM class
    """
    def __init__(self, osm_class: OpenStreetMapClass = OpenStreetMapClass.ALL, **kwargs):
        super().__init__(**kwargs)
        self.osm_class = osm_class

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None,
                 force_data_refresh=False):
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
            osm_feature.crs = WGS_CRS

        # Filter by geom_type
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


class OpenStreetMapAmenityCount(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["osm_class"]
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        osm_class: OSM class
    """
    def __init__(self, osm_class: OpenStreetMapClass = OpenStreetMapClass.ALL, convert_to_centroids=False, **kwargs):
        super().__init__(**kwargs)
        self.osm_class = osm_class
        self.convert_to_centroids = convert_to_centroids

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        # Note: spatial_resolution and resampling_method arguments are ignored.
        osm_data = OpenStreetMap(osm_class=self.osm_class).get_data(bbox)
        if self.convert_to_centroids:
            osm_data.geometry = osm_data.centroid
        else:
            osm_data = osm_data.dissolve().explode()  # Removing overlapping geoms to prevent memory error
        osm_data['amenitycount'] = 1
        osmdata_ee = geemap.gdf_to_ee(osm_data)
        osmcount_ras_ee = osmdata_ee.reduceToImage(properties=['amenitycount'], reducer=ee.Reducer.sum())

        # Get Worldpop raster for grid template
        ee_rectangle = bbox.to_ee_rectangle()
        worldpop = (
            ee.ImageCollection("WorldPop/GP/100m/pop")
            .filterBounds(ee_rectangle['ee_geometry'])
            .filter(ee.Filter.eq("year", 2020))
            .mosaic()
            .clip(ee_rectangle['ee_geometry'])
        )

        count_raster = get_image_collection(
            ee.ImageCollection(worldpop.gt(-1).multiply(osmcount_ras_ee)),
            ee_rectangle,
            spatial_resolution,
            "osm amenities"
        ).population

        if not self.convert_to_centroids:        # Add overlapping geoms back in
            intersection_gdf = osm_data.sjoin(osm_data)
            intersection_gdf = intersection_gdf.loc[intersection_gdf["id_left"] < intersection_gdf["id_right"]]  # Remove self-intersections and duplicates
            intersection_gdf["amenitycount"] = 1
            intersections_ee = geemap.gdf_to_ee(intersection_gdf)
            intersections_ras_ee = intersections_ee.reduceToImage(properties=['amenitycount'], reducer=ee.Reducer.sum())
            intersection_raster = get_image_collection(
                ee.ImageCollection(worldpop.gt(-1).multiply(intersections_ras_ee)),
                bbox.to_ee_rectangle(),
                spatial_resolution,
                "osm intersections"
            ).population

            count_raster += intersection_raster

        return count_raster
