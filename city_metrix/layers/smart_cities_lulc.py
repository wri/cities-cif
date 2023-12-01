from pystac_client import Client
import rioxarray
import xarray as xr
import ee

from .layer import Layer, get_utm_zone_epsg
from .. import EsaWorldCover, EsaWorldCoverClass
from .. import OpenStreetMap


class SmartCitiesLULC(Layer):
    def __init__(self, land_cover_class=None, **kwargs):
        super().__init__(**kwargs)
        self.land_cover_class = land_cover_class

    def get_data(self, bbox):
        esa1m = EsaWorldCover.get_data(bbox).rio.reproject(grid=())

        open_space_tag = {'leisure': ['park', 'nature_reserve', 'common', 'playground', 'pitch', 'track', 'garden', 'golf_course', 'dog_park', 'recreation_ground', 'disc_golf_course'],
                          'boundary': ['protected_area', 'national_park', 'forest_compartment', 'forest']}
        water_tag = {'water': True,
                     'natural': ['water'],
                     'waterway': True}
        roads_tag = {'highway': ["residential", "service", "unclassified", "tertiary", "secondary", "primary", "turning_circle", "living_street", "trunk", "motorway", "motorway_link", "trunk_link",
                                 "primary_link", "secondary_link", "tertiary_link", "motorway_junction", "turning_loop", "road", "mini_roundabout", "passing_place", "busway"]}
        building = {'building': True}
        parking = {'amenity': ['parking'],
                   'parking': True}

        osm_gdf = OpenStreetMap().get_data(bbox)
        crs = get_utm_zone_epsg(bbox)

        make_geocube(
            vector_data=osm_gdf,
            measurements=["index"],
            like=esa1m,
        )

       