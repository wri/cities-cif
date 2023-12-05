from enum import Enum
import osmnx as ox
import rasterio

from .layer import Layer, get_utm_zone_epsg


class OpenSpaceClass(Enum):
    leisure = ['park', 'nature_reserve', 'common', 'playground', 'pitch', 'track']
    boundary = ['protected_area', 'national_park']

    @classmethod
    def to_dict(cls):
        return {e.name: e.value for e in cls}


class OSMOpenSpace(Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox):
        north, south, east, west = bbox[3],  bbox[1], bbox[0], bbox[2]
        rec_sites = ox.features_from_bbox(north, south, east, west, OpenSpaceClass.to_dict())

        # Drop points & lines
        rec_sites = rec_sites[rec_sites.geom_type != 'Point']
        rec_sites = rec_sites[rec_sites.geom_type != 'LineString']

        return rec_sites.reset_index()

