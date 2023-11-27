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


class OsmOpenSpace(Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rec_sites = None

    def get_data(self, bbox, tags=None):
        # use bounding box to get geodataframe of all OSM data on recreation sites/parks
        self.rec_sites = ox.features_from_bbox(bbox['maxy'], bbox['miny'], bbox['maxx'], bbox['minx'], tags)

        # Drop points & lines
        self.rec_sites = self.rec_sites[self.rec_sites.geom_type != 'Point']
        self.rec_sites = self.rec_sites[self.rec_sites.geom_type != 'LineString']

        # Get the UTM zone projection for given a bounding box.
        proj = get_utm_zone_epsg(bbox)
        # Reproject to local UTM projection
        self.rec_sites = self.rec_sites.to_crs(proj)

    def rasterize_to(self, ref_res):
        if self.rec_sites is None or self.rec_sites.empty:
            raise ValueError("No data to rasterize. Please fetch data using get_data method first.")

        # Rasterize to match grid of referenced raster
        geom = [shapes for shapes in self.rec_sites.geometry]

        # Rasterize vector using the shape and coordinate system of the raster
        # all_touched = False means that only cells whose centroid is in the polygon are included
        # https://pygis.io/docs/e_raster_rasterize.html

        # Open space value is 10
        rasterized = rasterio.features.rasterize(
            geom,
            out_shape=ref_res.shape,
            fill=0,
            out=None,
            transform=ref_res.transform,
            all_touched=False,
            default_value=10,
            dtype=None
        )

        return rasterized
