import math

import ee
import shapely
import utm
import shapely.geometry as geometry
import geopandas as gpd

from typing import Union

from geopandas import GeoDataFrame
from shapely.geometry import point

from city_metrix.constants import WGS_CRS, GeoType, ProjectionType
from city_metrix.metrix_dao import get_city, get_city_boundary, get_city_admin_boundaries
from city_metrix.layers.layer_tools import get_projection_type, get_haversine_distance

MAX_SIDE_LENGTH_METERS = 50000 # This values should cover most situations
MAX_SIDE_LENGTH_DEGREES = 0.5 # Given that for latitude, 50000m * (1deg/111000m)

class GeoZone():
    def __init__(self, geo_zone:Union[GeoDataFrame | str], crs=WGS_CRS):
        if isinstance(geo_zone, str):
            self.geo_type = GeoType.CITY
        else:
            self.geo_type = GeoType.GEOMETRY

        if self.geo_type == GeoType.GEOMETRY:
            self.city_id = None
            self.city_json = None
            self.aoi_id = None
            self.admin_level = None
            self.zones = geo_zone
            self.bbox = geo_zone.total_bounds
        else:
            city_json = geo_zone
            city_id, aoi_id = _parse_city_aoi_json(city_json)
            city = get_city(city_id)
            admin_level = city.get(aoi_id, None)
            if not admin_level:
                raise ValueError(f"City metadata for {self.city_id} does not have geometry for admin_level: 'city_admin_level'")
            self.zones = get_city_admin_boundaries(city_id, admin_level)
            self.city_id = city_id
            self.aoi_id = aoi_id
            self.admin_level = admin_level
            epsg_code = self.zones.crs.to_epsg()
            crs = f'EPSG:{epsg_code}'
            bounds = self.zones.total_bounds
            if get_projection_type(crs) == ProjectionType.GEOGRAPHIC:
                self.bbox = bounds
            else:
                reproj_bbox = reproject_units(bounds[1], bounds[0], bounds[3], bounds[2], WGS_CRS, crs)
                self.bbox = (reproj_bbox[1], reproj_bbox[0], reproj_bbox[3], reproj_bbox[2])

        self.crs = crs
        self.bounds = self.bbox
        self.epsg_code = int(self.crs.split(':')[1])
        self.projection_type = get_projection_type(crs)
        self.units = "degrees" if self.projection_type == ProjectionType.GEOGRAPHIC else "meters"

        self.min_x = self.bbox[0]
        self.min_y = self.bbox[1]
        self.max_x = self.bbox[2]
        self.max_y = self.bbox[3]

        self.coords = (self.min_x, self.min_y, self.max_x, self.max_y)

        self.centroid = shapely.box(self.min_x, self.min_y, self.max_x, self.max_y).centroid

        self.polygon = shapely.box(self.min_x, self.min_y, self.max_x, self.max_y)


def _parse_city_aoi_json(json_str):
    import json
    data = json.loads(json_str)
    city_id = data['city_id']
    aoi_id = data['aoi_id']
    return city_id, aoi_id


def reproject_units(min_x, min_y, max_x, max_y, from_crs, to_crs):
    """
    Project coordinates from one map EPSG projection to another
    """
    from pyproj import Transformer
    transformer = Transformer.from_crs(from_crs, to_crs)

    # Note: order of coordinates must be lat/lon
    sw_coord = transformer.transform(min_x, min_y)
    ne_coord = transformer.transform(max_x, max_y)

    reproj_min_x = float(sw_coord[0])
    reproj_min_y = float(sw_coord[1])
    reproj_max_x = float(ne_coord[0])
    reproj_max_y = float(ne_coord[1])

    reproj_bbox = (reproj_min_y, reproj_min_x, reproj_max_y, reproj_max_x)
    return reproj_bbox

