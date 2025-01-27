import math
import ee
import shapely
import utm
import shapely.geometry as geometry
import geopandas as gpd

from shapely.geometry import box
from city_metrix.layers.layer import WGS_CRS

class LayerBbox():
    def __init__(self, bbox: tuple[float, float, float, float], crs:str=WGS_CRS):
        self.bbox = bbox

        self.crs = crs
        self.units = "degrees" if self.crs == WGS_CRS else "meters"

        self.min_x = bbox[0]
        self.min_y = bbox[1]
        self.max_x = bbox[2]
        self.max_y = bbox[3]

        self.centroid = box(self.min_x, self.min_y, self.max_x, self.max_y).centroid

        self.polygon = shapely.box(self.min_x, self.min_y, self.max_x, self.max_y)

        self.epsg_code = int(self.crs.split(':')[1])

        self. _validate_coordinates()

    def _validate_coordinates(self):
        if self.crs == WGS_CRS:
            if not (-180 <= self.min_x < self.max_y <= 180) and (-90 <= self.min_x < self.max_y <= 90):
                raise Exception(f'Coordinates are not in correct range for EPSG:4326 in bbox {self.bbox}')
        else:
            if not isinstance(self.crs, str) or not self.crs.startswith('EPSG:'):
                raise Exception("Valid crs must be specified in form of ('EPSG:n') where n is an EPSG code.")

            if not (32601 <= self.epsg_code <= 32660 or 32701 <= self.epsg_code <= 32760):
                e_msg = (f'Not a recognized valid UTM epsg_code ({self.crs}). '
                         f'EPSG code must be in: [32601 - 32660, 32701 - 32760]')
                raise Exception(e_msg)

    def to_ee_rectangle(self, output_as):
        """
        Converts bbox to an Earth Engine geometry rectangle
        :param output_as: specify projection for geometry values as (utm or latlon).
        :return:
        """
        valid_output_as = ('latlon', 'utm')
        if output_as not in valid_output_as:
            raise ValueError(f'output_as value must be in ({valid_output_as})')

        if self.crs == WGS_CRS and output_as=="latlon":
            ee_rectangle = _build_ee_rectangle(round(self.min_x,7), round(self.min_y,7),
                                            round(self.max_x,7), round(self.max_y,7),
                                            WGS_CRS)
            return ee_rectangle
        elif self.crs == WGS_CRS and output_as=="utm":
            utm_crs = get_utm_zone_from_latlon_point(self.centroid)
            utm_bbox = reproject_units(self.min_y, self.min_x, self.max_y, self.max_x, WGS_CRS, utm_crs)
            ee_rectangle = _build_ee_rectangle(round(utm_bbox[1],2), round(utm_bbox[0],2),
                                               round(utm_bbox[3],2), round(utm_bbox[2],2),
                                               utm_crs)
            return ee_rectangle
        elif self.crs != WGS_CRS and output_as=="latlon":
            utm_crs = self.crs
            latlon_bbox = reproject_units(self.min_x, self.min_y, self.max_x, self.max_y, utm_crs, WGS_CRS)
            ee_rectangle = _build_ee_rectangle(round(latlon_bbox[0],7), round(latlon_bbox[1],7),
                                               round(latlon_bbox[2],7), round(latlon_bbox[3],7),
                                               WGS_CRS)
            return ee_rectangle
        elif self.crs != WGS_CRS and output_as == "utm":
            ee_rectangle = _build_ee_rectangle(round(self.min_x,2), round(self.min_y,2),
                                            round(self.max_x,2), round(self.max_y,2),
                                            self.crs)
            return ee_rectangle
        else:
            raise Exception("invalid request to to_ee_rectangle")


    def as_utm_bbox(self):
        """
        Converts bbox to UTM projection
        :return:
        """
        if self.crs == WGS_CRS:
            utm_crs = get_utm_zone_from_latlon_point(self.centroid)
            reproj_bbox = reproject_units(self.min_y, self.min_x, self.max_y, self.max_x, WGS_CRS, utm_crs)
            # round to minimize drift
            utm_box = (round(reproj_bbox[1],2), round(reproj_bbox[0],2), round(reproj_bbox[3],2), round(reproj_bbox[2],2))
            bbox = LayerBbox(bbox=utm_box, crs=utm_crs)
            return bbox
        else:
            return self

    def as_lat_lon_bbox(self):
        """
        Converts bbox to lat-lon bbox
        :return:
        """
        if self.crs == WGS_CRS:
            return self
        else:
            reproj_bbox = reproject_units(self.min_x, self.min_y, self.max_x, self.max_y, self.crs, WGS_CRS)
            # round to minimize drift
            box = (round(reproj_bbox[0],7), round(reproj_bbox[1],7), round(reproj_bbox[2],7), round(reproj_bbox[3],7))
            bbox = LayerBbox(bbox=box, crs=WGS_CRS)
            return bbox

def _build_ee_rectangle(min_x, min_y, max_x, max_y, crs):
    ee_rectangle = ee.Geometry.Rectangle(
        [min_x, min_y, max_x, max_y],
        crs,
        geodesic=False
    )
    rectangle = {"ee_geometry": ee_rectangle, "crs": crs}
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


def get_utm_zone_from_latlon_point(centroid) -> str:
    """
    Get the UTM zone projection for given a bounding box.

    :param bbox: tuple of (min x, min y, max x, max y)
    :return: the EPSG code for the UTM zone of the centroid of the bbox
    """

    utm_x, utm_y, band, zone = utm.from_latlon(centroid.y, centroid.x)

    if centroid.y > 0:  # Northern zone
        epsg = 32600 + band
    else:
        epsg = 32700 + band

    return f"EPSG:{epsg}"


def create_fishnet_grid(bbox:LayerBbox,
                        tile_side_length:float=0, tile_buffer_size:float=0, length_units:str="meters",
                        spatial_resolution:int=1, output_as:str="utm"):
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

    valid_output = ['utm', 'latlon']
    if output_as not in valid_output:
        raise ValueError(f"Invalid grid_units ('{output_as}'). "
                         f"Valid methods: [{valid_output}]")

    if length_units == "degrees":
        if tile_side_length < 0.001:
            raise ValueError('Value for tile_side_length is too small.')
        if tile_side_length > 0.5:
            raise ValueError('Value for tile_side_length is too large.')
    else:
        if tile_side_length < 10:
            raise ValueError('Value for tile_side_length is too small.')
        if tile_side_length > 5000:
            raise ValueError('Value for tile_side_length is too large.')

    x_tile_side_units, y_tile_side_units, tile_buffer_units =\
        _get_offsets(bbox, tile_side_length, tile_buffer_size, length_units, spatial_resolution, output_as)

    start_x_coord, start_y_coord, end_x_coord, end_y_coord = _get_bounding_coords(bbox, output_as)

    x_cell_count = round((end_x_coord - start_x_coord) / x_tile_side_units, 0)
    y_cell_count = round((end_y_coord - start_y_coord) / y_tile_side_units, 0)
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


    if bbox.crs == WGS_CRS and output_as== "latlon":
        grid_crs = WGS_CRS
    elif bbox.crs == WGS_CRS and output_as== "utm":
        grid_crs = get_utm_zone_from_latlon_point(bbox.centroid)
    else:
        grid_crs = bbox.crs

    fishnet = gpd.GeoDataFrame(geom_array, columns=["geometry"]).set_crs(grid_crs)
    fishnet["fishnet_geometry"] = fishnet["geometry"]
    return fishnet

def _truncate_to_nearest_interval(tile_side_meters, spatial_resolution):
    floor_increment = (tile_side_meters // spatial_resolution) * spatial_resolution
    ceil_increment = -(-tile_side_meters // spatial_resolution) * spatial_resolution
    floor_offset = abs(floor_increment - tile_side_meters)
    ceil_offset = abs(ceil_increment - tile_side_meters)
    nearest_increment = floor_increment if floor_offset < ceil_offset else ceil_increment

    return nearest_increment

def _get_offsets(bbox, tile_side_length, tile_buffer_size, length_units, spatial_resolution, output_as):
    if output_as=="latlon":
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
    if output_as == 'latlon':
        if bbox.units == "degrees":
            start_x_coord, start_y_coord = (bbox.min_x, bbox.min_y)
            end_x_coord, end_y_coord = (bbox.max_x, bbox.max_y)
        else: #meters
            raise Exception("Currently does not support length_units in meters and output_as latlon")
    else: # projected
        if bbox.units == "degrees":
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


def _get_degree_offsets_for_meter_units(bbox: LayerBbox, tile_side_degrees):
    if bbox.crs != WGS_CRS:
        raise ValueError("Bbox must have WGS crs")

    mid_x = (bbox.min_x + bbox.min_x) / 2
    x_offset = get_haversine_distance(mid_x, bbox.min_y, mid_x + tile_side_degrees, bbox.min_y)

    mid_y = (bbox.min_y + bbox.min_y) / 2
    y_offset = get_haversine_distance(bbox.min_x, mid_y, bbox.min_x, mid_y + tile_side_degrees)

    return x_offset, y_offset


def get_haversine_distance(lon1, lat1, lon2, lat2):
    # Global-average radius of the Earth in meters
    R = 6371000

    # Convert degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in meters
    distance = R * c

    return distance
