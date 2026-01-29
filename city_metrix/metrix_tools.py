import math
from typing import Union

import numpy as np
import rasterio
import rioxarray
import utm
from pyproj import CRS
from rasterio.warp import Resampling, reproject
from shapely.geometry import point

from city_metrix.constants import WGS_EPSG_CODE, ProjectionType


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

def get_projection_type(crs: Union[str | int]):
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


# def meters_to_approximate_degrees(meters):
#     # Earth's radius in meters
#     earth_radius = 6371000
#     # Convert meters to degrees
#     degrees = (meters / (2 * math.pi * earth_radius)) * 360
#     return degrees


def buffer_bbox(lat_min, lon_min, lat_max, lon_max, buffer_meters):
    # Approximate conversion from meters to degrees at a given latitude
    def meters_to_degrees_lat(meters):
        return meters / 111320

    def meters_to_degrees_lon(meters, latitude):
        return meters / (111320 * math.cos(math.radians(latitude)))

    # Use center latitude to approximate longitude degree size
    center_lat = (lat_min + lat_max) / 2

    lat_buffer = meters_to_degrees_lat(buffer_meters)
    lon_buffer = meters_to_degrees_lon(buffer_meters, center_lat)

    return (
        lat_min - lat_buffer,
        lon_min - lon_buffer,
        lat_max + lat_buffer,
        lon_max + lon_buffer
    )

def is_date(string):
    from dateutil.parser import parse
    if string is None:
        return False

    try:
        parse(string, False)
        return True
    except ValueError:
        return False


def is_openurban_available_for_city(city_id):
    import ee
    import xee

    ic = ee.ImageCollection("projects/wri-datalab/cities/OpenUrban/OpenUrban_LULC")
    store = xee.EarthEngineStore(ic, ee_init_if_necessary=True)

    is_available = False
    for image_id in store.image_ids:
        # Split the string by '/' and take the last part
        last_part = image_id.split('/')[-1]
        city_name = _get_city_part_of_openurban_file_name(last_part)
        if city_name == city_id:
            is_available = True
            break
    return is_available

def _get_city_part_of_openurban_file_name(s):
    import re

    # This pattern matches an underscore followed by one or more digits
    return re.sub(r'_\d+', '', s)


def align_raster_array(raster_array, ref_array):
    """
    1. Computes weighted average of raster for the ref grid.
    2. Identifies 'gaps' (NoData) that occurred at the edges.
    3. Fills those specific gaps using Nearest Neighbor (taking the pixel it falls under).
    """
    ref_path = "temp_ref_raster.tif"
    ref_array.rio.to_raster(raster_path=ref_path, driver="GTiff")
    
    raster_path = "temp_raster.tif"
    raster_array.rio.to_raster(raster_path=raster_path, driver="GTiff")

    output_path = "temp_output_raster.tif"

    with rasterio.open(ref_path) as ref_ds:
        ref_data = ref_ds.read(1)
        ref_meta = ref_ds.profile.copy()
        ref_transform = ref_ds.transform
        ref_crs = ref_ds.crs
        ref_nodata = ref_ds.nodata if ref_ds.nodata is not None else -999
        
        target_valid_mask = (ref_data != ref_nodata)

    with rasterio.open(raster_path) as src_ds:
        src_nodata = src_ds.nodata if src_ds.nodata is not None else -999
        
        out_data = np.full(ref_data.shape, np.nan, dtype='float32')

        print("Pass 1: Computing Average...")
        reproject(
            source=rasterio.band(src_ds, 1),
            destination=out_data,
            src_transform=src_ds.transform,
            src_crs=src_ds.crs,
            dst_transform=ref_transform,
            dst_crs=ref_crs,
            resampling=Resampling.average, # Strict averaging
            src_nodata=src_nodata,
            dst_nodata=np.nan # Use NaN temporarily for easier math
        )

        gaps_mask = target_valid_mask & np.isnan(out_data)
        
        if np.any(gaps_mask):
            print(f"Pass 2: Filling {np.sum(gaps_mask)} gap pixels using Nearest Neighbor...")
            
            # Create a temporary array just for the nearest neighbor values
            nearest_fill = np.full(ref_data.shape, np.nan, dtype='float32')
            
            reproject(
                source=rasterio.band(src_ds, 1),
                destination=nearest_fill,
                src_transform=src_ds.transform,
                src_crs=src_ds.crs,
                dst_transform=ref_transform,
                dst_crs=ref_crs,
                resampling=Resampling.nearest, # FORCE value capture
                src_nodata=src_nodata,
                dst_nodata=np.nan
            )
            
            out_data[gaps_mask] = nearest_fill[gaps_mask]

        final_nodata_value = -999
        out_data = np.where(np.isnan(out_data), final_nodata_value, out_data)

        ref_meta.update({
            'driver': 'GTiff',
            'dtype': 'float32',
            'nodata': final_nodata_value,
            'count': 1
        })

        with rasterio.open(output_path, 'w', **ref_meta) as dst:
            dst.write(out_data, 1)
            print(f"Success. Saved gap-filled raster to: {output_path}")

    return rioxarray.open_rasterio(output_path).squeeze()
