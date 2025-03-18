import math

import ee
import shapely
import utm
import shapely.geometry as geometry
import geopandas as gpd
from typing import Union

from shapely.geometry import point

from city_metrix.constants import WGS_CRS
from city_metrix.layers.layer_tools import get_projection_name, get_haversine_distance, get_city, get_city_boundary, \
    get_geojson_df_bounds

MAX_SIDE_LENGTH_METERS = 50000 # This values should cover most situations
MAX_SIDE_LENGTH_DEGREES = 0.5 # Given that for latitude, 50000m * (1deg/111000m)

class GeoExtent():
    def __init__(self, bbox:Union[tuple[float, float, float, float]|str], crs=WGS_CRS):
        if isinstance(bbox, str):
            self.geo_extent_type = 'city_id'
        else:
            self.geo_extent_type = 'geometry'

        if self.geo_extent_type == 'geometry':
            self.bbox = bbox
        else:
            city_json = bbox
            city_id, aoi_id = _parse_city_aoi_json(city_json)
            city = get_city(city_id)
            admin_level = city.get(aoi_id)
            if not admin_level:
                raise ValueError(f"City metadata for {city_id} does not have geometry for admin_level: 'city_admin_level'")
            city_boundary = get_city_boundary(city_id, admin_level)
            bbox = get_geojson_df_bounds(city_boundary)
            if get_projection_name(crs) == 'geographic':
                self.bbox = bbox
            else:
                reproj_bbox = reproject_units(bbox[1], bbox[0], bbox[3], bbox[2], WGS_CRS, crs)
                self.bbox = (reproj_bbox[1], reproj_bbox[0], reproj_bbox[3], reproj_bbox[2])

        self.crs = crs
        self.bounds = self.bbox
        self.epsg_code = int(self.crs.split(':')[1])
        self.projection_name = get_projection_name(crs)
        self.units = "degrees" if self.projection_name == 'geographic' else "meters"

        self.min_x = self.bbox[0]
        self.min_y = self.bbox[1]
        self.max_x = self.bbox[2]
        self.max_y = self.bbox[3]

        self.coords = (self.min_x, self.min_y, self.max_x, self.max_y)

        self.centroid = shapely.box(self.min_x, self.min_y, self.max_x, self.max_y).centroid

        self.polygon = shapely.box(self.min_x, self.min_y, self.max_x, self.max_y)


    def to_ee_rectangle(self):
        """
        Converts bbox to an Earth Engine geometry rectangle
        """
        if self.projection_name == 'geographic':
            utm_bbox = self.as_utm_bbox()
            minx, miny, maxx, maxy = utm_bbox.bounds
            ee_rectangle = _build_ee_rectangle(minx, miny, maxx, maxy, utm_bbox.crs)
        elif self.projection_name == 'utm':
            ee_rectangle = _build_ee_rectangle(self.min_x, self.min_y, self.max_x, self.max_y, self.crs)
        else:
            raise Exception("invalid request to to_ee_rectangle")

        return ee_rectangle


    def as_utm_bbox(self):
        """
        Converts bbox to UTM projection
        :return:
        """
        if self.projection_name == 'geographic':
            utm_crs = get_utm_zone_from_latlon_point(self.centroid)
            reproj_bbox = reproject_units(self.min_y, self.min_x, self.max_y, self.max_x, WGS_CRS, utm_crs)
            # round to minimize drift
            utm_box = (reproj_bbox[1], reproj_bbox[0], reproj_bbox[3], reproj_bbox[2])
            bbox = GeoExtent(bbox=utm_box, crs=utm_crs)
            return bbox
        else:
            return self

    def as_geographic_bbox(self):
        """
        Converts bbox to lat-lon bbox
        :return:
        """
        if self.projection_name == 'geographic':
            return self
        else:
            reproj_bbox = reproject_units(self.min_x, self.min_y, self.max_x, self.max_y, self.crs, WGS_CRS)
            # round to minimize drift
            box = (reproj_bbox[0], reproj_bbox[1], reproj_bbox[2], reproj_bbox[3])
            bbox = GeoExtent(bbox=box, crs=WGS_CRS)
            return bbox

def _parse_city_aoi_json(json_str):
    import json
    data = json.loads(json_str)
    city_id = data['city_id']
    aoi_id = data['aoi_id']
    return city_id, aoi_id

def _buffer_coordinates(minx, miny, maxx, maxy):
    buffer_distance_m = 10
    buf_minx = minx - buffer_distance_m
    buf_miny = miny - buffer_distance_m
    buf_maxx = maxx + buffer_distance_m
    buf_maxy = maxy + buffer_distance_m
    return buf_minx, buf_miny, buf_maxx, buf_maxy

def _build_ee_rectangle(min_x, min_y, max_x, max_y, crs):
    # Snap coordinates to lower 1-meter on all sides so that adjacent tiles align to each other.
    minx = float(math.floor(min_x))
    miny = float(math.floor(min_y))
    maxx = float(math.floor(max_x))
    maxy = float(math.floor(max_y))
    source_bounds = (minx, miny, maxx, maxy)

    buf_minx, buf_miny, buf_maxx, buf_maxy = _buffer_coordinates(minx, miny, maxx, maxy)

    ee_rectangle = ee.Geometry.Rectangle(
        [buf_minx, buf_miny, buf_maxx, buf_maxy],
        crs,
        geodesic=False
    )

    rectangle = {"ee_geometry": ee_rectangle, "bounds": source_bounds, "crs": crs}
    return rectangle



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


def get_utm_zone_from_latlon_point(sample_point: point) -> str:
    """
    Get the UTM zone projection for given geographic point.
    :param sample_point: a shapely point specified in geographic coordinates
    :return: the crs (EPSG code) for the UTM zone of the point
    """

    utm_x, utm_y, band, zone = utm.from_latlon(sample_point.y, sample_point.x)

    if sample_point.y > 0:  # Northern zone
        epsg = 32600 + band
    else:
        epsg = 32700 + band

    return f"EPSG:{epsg}"


def create_fishnet_grid(bbox:GeoExtent,
                        tile_side_length:float=0, tile_buffer_size:float=0, length_units:str="meters",
                        spatial_resolution:int=1, output_as:str="utm") -> gpd.GeoDataFrame:
    """
    Constructs a grid of tiled areas in either geographic or utm space.
    :param bbox: bounding dimensions of the enclosing box around the grid.
    :param tile_side_length: tile size in specified units. Max is 10000m or approx. 0.1 degrees.
    :param tile_buffer_size: buffer size in specified units.
    :param length_units: units for tile_side_length and tile_buffer_size in either "meters" or "degrees".
    :param spatial_resolution: distance in meters for incremental spacing of the tile size.
    :param output_as: reference system in which the grid is constructed. either "utm" or "geographic".
    :return: GeoDataFrame
    """
    # NOTE: the AOI can be specified in either WGS or UTM, but the generated tile grid is always in UTM
    tile_side_length = 0 if tile_side_length is None else tile_side_length
    tile_buffer_size = 0 if tile_buffer_size is None else tile_buffer_size
    spatial_resolution = 1 if spatial_resolution is None else spatial_resolution

    if length_units is None:
        if (tile_side_length > 0 or tile_buffer_size > 0):
            raise Exception("Length_units cannot be None if tile_side_length or tile_buffer_size are > 0")
        else:
            length_units = "meters" # a placeholder value

    length_units = length_units.lower()
    output_as = 'utm' if output_as is None else output_as.lower()

    valid_length_units = ['degrees', 'meters']
    if length_units not in valid_length_units:
        raise ValueError(f"Invalid length_units ('{length_units}'). "
                         f"Valid methods: [{valid_length_units}]")

    valid_output = ['utm', 'geographic']
    if output_as not in valid_output:
        raise ValueError(f"Invalid grid_units ('{output_as}'). "
                         f"Valid methods: [{valid_output}]")

    if length_units == "degrees":
        if tile_side_length > MAX_SIDE_LENGTH_DEGREES:
            raise ValueError('Value for tile_side_length is too large.')
    else:
        if tile_side_length > MAX_SIDE_LENGTH_METERS:
            raise ValueError('Value for tile_side_length is too large.')

    x_tile_side_units, y_tile_side_units, tile_buffer_units =\
        _get_offsets(bbox, tile_side_length, tile_buffer_size, length_units, spatial_resolution, output_as)

    start_x_coord, start_y_coord, end_x_coord, end_y_coord = _get_bounding_coords(bbox, output_as)

    # Restrict the cell size to something reasonable
    x_cell_count = math.floor((end_x_coord - start_x_coord) / x_tile_side_units)
    y_cell_count = math.floor((end_y_coord - start_y_coord) / y_tile_side_units)
    if x_cell_count > 100:
        raise ValueError('Failure. Grid would have too many cells along the x axis.')
    if y_cell_count > 100:
        raise ValueError('Failure. Grid would have too many cells along the y axis.')

    geom_array = []
    x_coord = start_x_coord
    y_coord = start_y_coord
    while y_coord < end_y_coord:
        while x_coord < end_x_coord:
            geom = _build_tile_geometry(x_coord, y_coord, x_tile_side_units, y_tile_side_units, tile_buffer_units)
            geom_array.append(geom)
            x_coord += x_tile_side_units
        x_coord = start_x_coord

        y_coord += y_tile_side_units

    if bbox.projection_name == 'geographic' and output_as == 'geographic':
        grid_crs = WGS_CRS
    elif bbox.projection_name == 'geographic' and output_as== "utm":
        grid_crs = get_utm_zone_from_latlon_point(bbox.centroid)
    else:
        grid_crs = bbox.crs

    fishnet = gpd.GeoDataFrame(geom_array, columns=["geometry"]).set_crs(grid_crs)
    fishnet["fishnet_geometry"] = fishnet["geometry"]
    return fishnet

def _truncate_to_nearest_interval(tile_side_meters, spatial_resolution):
    # Snap the cell increment to the closest whole increment
    floor_increment = math.floor((tile_side_meters / spatial_resolution)) * spatial_resolution
    ceil_increment = math.ceil((tile_side_meters / spatial_resolution)) * spatial_resolution

    floor_offset = abs(floor_increment - tile_side_meters)
    ceil_offset = abs(ceil_increment - tile_side_meters)
    nearest_increment = floor_increment if floor_offset < ceil_offset else ceil_increment

    return nearest_increment

def _get_offsets(bbox, tile_side_length, tile_buffer_size, length_units, spatial_resolution, output_as):
    if output_as=='geographic':
        if length_units == "degrees":
            x_tile_side_units = y_tile_side_units = tile_side_length

            tile_buffer_units = tile_buffer_size
        else: #meters
            raise Exception("Currently does not support length_units in meters and output_as latlon")
    else: # projected
        if length_units=="degrees":
            x_tile_side_meters, y_tile_side_meters = _get_degree_offsets_for_meter_units(bbox, tile_side_length)
            x_tile_side_units = _truncate_to_nearest_interval(x_tile_side_meters, spatial_resolution)
            y_tile_side_units = _truncate_to_nearest_interval(y_tile_side_meters, spatial_resolution)

            avg_side_meters = (x_tile_side_meters + y_tile_side_meters)/2
            tile_buffer_units = avg_side_meters * (tile_buffer_size/tile_side_length)
        else: # meters
            tile_side_meters= _truncate_to_nearest_interval(tile_side_length, spatial_resolution)
            x_tile_side_units = y_tile_side_units = tile_side_meters

            tile_buffer_units = tile_buffer_size

    return x_tile_side_units, y_tile_side_units, tile_buffer_units


def _get_bounding_coords(bbox, output_as):
    if output_as == 'geographic':
        if bbox.projection_name == 'geographic':
            start_x_coord, start_y_coord = (bbox.min_x, bbox.min_y)
            end_x_coord, end_y_coord = (bbox.max_x, bbox.max_y)
        else: #meters
            raise Exception("Currently does not support length_units in meters and output_as latlon")
    else: # projected
        if bbox.projection_name == 'geographic':
            project_bbox = bbox.as_utm_bbox()
            start_x_coord, start_y_coord = (project_bbox.min_x, project_bbox.min_y)
            end_x_coord, end_y_coord = (project_bbox.max_x, project_bbox.max_y)
        else: # meters
            start_x_coord, start_y_coord = (bbox.min_x, bbox.min_y)
            end_x_coord, end_y_coord = (bbox.max_x, bbox.max_y)

    return start_x_coord, start_y_coord, end_x_coord, end_y_coord


def _build_tile_geometry(x_coord, y_coord, x_tile_side_units, y_tile_side_units, tile_buffer_units):
    cell_min_x = x_coord - tile_buffer_units
    cell_min_y = y_coord - tile_buffer_units
    cell_max_x = x_coord + x_tile_side_units + tile_buffer_units
    cell_max_y = y_coord + y_tile_side_units + tile_buffer_units

    geom = geometry.Polygon(
        [
            (cell_min_x, cell_min_y),
            (cell_min_x, cell_max_y),
            (cell_max_x, cell_max_y),
            (cell_max_x, cell_min_y),
            (cell_min_x, cell_min_y),
        ]
    )
    return geom


def _get_degree_offsets_for_meter_units(bbox: GeoExtent, tile_side_degrees):
    if bbox.projection_name != 'geographic':
        raise ValueError(f"Bbox must have CRS set to {WGS_CRS}")

    mid_x = (bbox.min_x + bbox.max_x) / 2
    x_offset = get_haversine_distance(mid_x, bbox.min_y, mid_x + tile_side_degrees, bbox.min_y)

    mid_y = (bbox.min_y + bbox.max_y) / 2
    y_offset = get_haversine_distance(bbox.min_x, mid_y, bbox.min_x, mid_y + tile_side_degrees)

    return x_offset, y_offset
