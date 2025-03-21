import math
import os

import geopandas as gpd
from typing import Union
from pyproj import CRS

from city_metrix.constants import WGS_EPSG_CODE

def set_environment_variable(variable_name, variable_value):
    os.environ[variable_name] = variable_value

def get_geojson_geometry_bounds(geojson: str):
    gdf = gpd.GeoDataFrame.from_features(geojson)
    return gdf.total_bounds


def get_projection_name(crs: Union[str|int]):
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
        projection_name = 'geographic'
    elif 32601 <= epsg_code <= 32660 or 32701 <= epsg_code <= 32760:
        projection_name = 'utm'
    else:
        raise ValueError(f"CRS ({crs}) not supported.")

    return projection_name

def standardize_y_dimension_direction(data_array):
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


