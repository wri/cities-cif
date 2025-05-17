import math
import utm
from typing import Union
from pyproj import CRS
from shapely.geometry import point

from city_metrix.constants import WGS_EPSG_CODE, ProjectionType
from typing import Union

def parse_city_aoi_json(json_str):
    import json
    data = json.loads(json_str)
    city_id = data['city_id']
    aoi_id = data['aoi_id']
    return city_id, aoi_id

def construct_city_aoi_json(city_id, aoi_id):
    json_str = f'{{"city_id": "{city_id}", "aoi_id": "{aoi_id}"}}'
    return json_str

# ================= Projection related =====================
def get_crs_from_data(data):
    crs_wkt = data.spatial_ref.crs_wkt
    epsg_code = CRS.from_wkt(crs_wkt).to_epsg()
    crs = f'EPSG:{epsg_code}'
    return crs

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

def get_projection_type(crs: Union[str, int]):
    if isinstance(crs, str):
        if crs.lower().startswith('epsg:'):
            epsg_code = int(crs.split(':')[1])
        else:
            try:
                epsg_code = CRS.from_wkt(crs).to_epsg()
            except:
                raise Exception("Valid crs string must be specified in form of ('EPSG:n') or a crs-wkt.")

    elif isinstance(crs, int):
        epsg_code = crs
    else:
        raise ValueError(f"Value of ({crs}) is an invalid crs string or epsg code. ")

    if epsg_code == WGS_EPSG_CODE:
        projection_type = ProjectionType.GEOGRAPHIC
    elif 32601 <= epsg_code <= 32660 or 32701 <= epsg_code <= 32760:
        projection_type = ProjectionType.UTM
    else:
        raise ValueError(f"CRS ({crs}) not supported.")

    return projection_type

#  ================ Misc ======================
def standardize_y_dimension_direction(data_array):
    """
    Function resets y-values so they comply with the standard GDAL top-down increasing order, as needed.
    """
    was_reversed= False
    y_dimensions = data_array.shape[0]
    if data_array.y.data[0] < data_array.y.data[y_dimensions - 1]:
        data_array = data_array.isel({data_array.rio.y_dim: slice(None, None, -1)})
        was_reversed = True
    return was_reversed, data_array

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


def get_class_from_instance(obj):
    cls = obj.__class__()
    return cls
