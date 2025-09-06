import math
import os
import random
import shutil
import subprocess
import tempfile
import time

import dask
import geopandas as gpd
import xarray as xr
import numpy as np
import pandas as pd
import ee
import shapely

from abc import abstractmethod
from pathlib import Path
from typing import Union
from dask.diagnostics import ProgressBar
from ee import ImageCollection
from geocube.api.core import make_geocube
from geopandas import GeoDataFrame
from pandas import Series
from shapely import geometry
from shapely.geometry import box
from xrspatial import zonal_stats

from city_metrix import s3_client
from city_metrix.cache_manager import retrieve_city_cache, build_file_key
from city_metrix.constants import WGS_CRS, ProjectionType, GeoType, GEOJSON_FILE_EXTENSION, CSV_FILE_EXTENSION, \
    DEFAULT_PRODUCTION_ENV, DEFAULT_DEVELOPMENT_ENV, GTIFF_FILE_EXTENSION, CIF_CACHE_S3_BUCKET_URI
from city_metrix.metrix_dao import (write_tile_grid, write_layer, write_metric,
                                    get_city, get_city_admin_boundaries, read_geotiff_from_cache, extract_tif_subarea,
                                    create_uri_target_folder, write_geojson, write_json, get_key_from_s3_uri,
                                    get_file_key_from_url, get_bucket_name_from_s3_uri,
                                    delete_s3_folder_if_exists, delete_s3_file_if_exists, get_file_path_from_uri)
from city_metrix.metrix_tools import (get_projection_type, get_haversine_distance, get_utm_zone_from_latlon_point,
                                      parse_city_aoi_json, reproject_units, construct_city_aoi_json,
                                      standardize_y_dimension_direction)

TILE_NUMBER_PADCOUNT = 5
MAX_RASTER_BYTES_FOR_SINGLE_FILE_OUTPUT = 500000000 # (Note: Teresina FabDem 544997973)
dask.config.set({'logging.distributed': 'warning'})

class GeoZone():
    def __init__(self, geo_zone: Union[GeoDataFrame | str], crs=WGS_CRS):
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
            if hasattr(geo_zone, 'total_bounds'):
                self.bbox = geo_zone.total_bounds
            else:
                self.bbox = geo_zone.bounds

            self.crs = crs
        else:
            city_json = geo_zone
            self.city_id, self.aoi_id = parse_city_aoi_json(city_json)
            # Boundaries from city_id and aoi_id
            city_data = get_city(self.city_id)
            if self.aoi_id == 'urban_extent':
                self.admin_level = self.aoi_id
            elif self.aoi_id == 'city_admin_level':
                self.admin_level = city_data.get(self.aoi_id, None)
            else:
                raise ValueError(
                    f"City metadata for {self.city_id} does not have geometry for aoi_id: '{self.aoi_id}'")

            # get city bbox from composite of admin areas and project
            # bbox is always projected to UTM
            self.bbox, self.crs, self.zones = _build_aoi_from_city_boundaries(self.city_id, self.admin_level, city_data)

        self.bounds = self.bbox
        self.epsg_code = int(self.crs.split(':')[1])
        self.projection_type = get_projection_type(self.crs)
        self.units = "degrees" if self.projection_type == ProjectionType.GEOGRAPHIC else "meters"

        self.min_x = self.bbox[0]
        self.min_y = self.bbox[1]
        self.max_x = self.bbox[2]
        self.max_y = self.bbox[3]

        self.coords = (self.min_x, self.min_y, self.max_x, self.max_y)
        self.polygon = shapely.box(self.min_x, self.min_y, self.max_x, self.max_y)
        self.centroid = self.polygon.centroid


def _build_aoi_from_city_boundaries(city_id, admin_level, city_data):
    if admin_level == 'urban_extent':
        bbox_str = city_data['bounding_box']['urban_extent']
        wgs_bbox = string_to_float_list(bbox_str)
        west, south, east, north = wgs_bbox
        boundaries_gdf = None
    else:
        # Construct bbox from total bounds of all admin levels
        boundaries_gdf = get_city_admin_boundaries(city_id)
        if len(boundaries_gdf) == 1:
            west, south, east, north = boundaries_gdf.bounds
        else:
            west, south, east, north = boundaries_gdf.total_bounds

    # determine UTM CRS
    centroid = shapely.box(west, south, east, north).centroid
    utm_crs = get_utm_zone_from_latlon_point(centroid)

    # reproject geodataframe to UTM
    if admin_level == 'urban_extent':
        bbox = reproject_units(south, west, north, east, WGS_CRS, utm_crs)
        reproj_south, reproj_west, reproj_north, reproj_east = bbox
        zones = None
    else:
        zones = boundaries_gdf.to_crs(utm_crs)
        if len(boundaries_gdf) == 1:
            reproj_west, reproj_south, reproj_east, reproj_north = zones.bounds
        else:
            reproj_west, reproj_south, reproj_east, reproj_north = zones.total_bounds

    # Round coordinates to whole units
    bbox = (math.floor(reproj_west), math.floor(reproj_south), math.ceil(reproj_east), math.ceil(reproj_north))

    return bbox, utm_crs, zones


class GeoExtent():
    def __init__(self, bbox: Union[tuple[float, float, float, float] | GeoZone | str], crs=WGS_CRS):
        if isinstance(bbox, str) or (isinstance(bbox, GeoZone) and bbox.geo_type == GeoType.CITY):
            self.geo_type = GeoType.CITY
        else:
            self.geo_type = GeoType.GEOMETRY

        if self.geo_type == GeoType.GEOMETRY:
            self.city_id = None
            self.aoi_id = None
            self.admin_level = None
            if isinstance(bbox, GeoZone):
                self.bbox = bbox.bbox
            elif isinstance(bbox, GeoDataFrame):
                self.bbox = bbox.total_bounds
            else:
                self.bbox = bbox
            if hasattr(bbox, 'crs'):
                box_crs = bbox.crs
                if hasattr(box_crs, 'srs'):
                    self.crs = box_crs.srs
                else:
                    self.crs = box_crs
            else:
                self.crs = crs

            self.epsg_code = int(self.crs.split(':')[1])
            self.projection_type = get_projection_type(self.crs)
            self.units = "degrees" if self.projection_type == ProjectionType.GEOGRAPHIC else "meters"
            self.bounds = self.bbox

            self.min_x = self.bbox[0]
            self.min_y = self.bbox[1]
            self.max_x = self.bbox[2]
            self.max_y = self.bbox[3]

            self.coords = (self.min_x, self.min_y, self.max_x, self.max_y)
            self.centroid = shapely.box(self.min_x, self.min_y, self.max_x, self.max_y).centroid
            self.polygon = shapely.box(self.min_x, self.min_y, self.max_x, self.max_y)

        else:
            geo_zone = bbox if isinstance(bbox, GeoZone) else GeoZone(geo_zone=bbox)
            self.city_id = geo_zone.city_id
            self.aoi_id = geo_zone.aoi_id
            self.admin_level = geo_zone.admin_level
            self.bbox = geo_zone.bbox
            self.crs = geo_zone.crs
            self.epsg_code = geo_zone.epsg_code
            self.projection_type = geo_zone.projection_type
            self.units = geo_zone.units
            self.bounds = geo_zone.bounds
            self.min_x, self.min_y, self.max_x, self.max_y = geo_zone.bounds
            self.coords = geo_zone.coords
            self.centroid = geo_zone.centroid
            self.polygon = geo_zone.polygon


    def to_ee_rectangle(self):
        """
        Converts bbox to an Earth Engine geometry rectangle
        """
        if self.projection_type == ProjectionType.GEOGRAPHIC:
            utm_bbox = self.as_utm_bbox()
            minx, miny, maxx, maxy = utm_bbox.bounds
            ee_rectangle = GeoExtent._build_ee_rectangle(minx, miny, maxx, maxy, utm_bbox.crs)
        elif self.projection_type == ProjectionType.UTM:
            ee_rectangle = GeoExtent._build_ee_rectangle(self.min_x, self.min_y, self.max_x, self.max_y, self.crs)
        else:
            raise Exception("invalid request to to_ee_rectangle")

        return ee_rectangle

    def buffer_utm_bbox(self, buffer_m):
        minx, miny, maxx, maxy = self.as_utm_bbox().bounds
        utm_crs = self.as_utm_bbox().crs
        buf_minx = minx - buffer_m
        buf_miny = miny - buffer_m
        buf_maxx = maxx + buffer_m
        buf_maxy = maxy + buffer_m
        buf_bbox = GeoExtent(bbox=(buf_minx, buf_miny, buf_maxx, buf_maxy), crs=utm_crs)
        return buf_bbox

    @staticmethod
    def _build_ee_rectangle(min_x, min_y, max_x, max_y, crs):
        # Snap coordinates to lower 1-meter on all sides so that adjacent tiles align to each other.
        minx = float(math.floor(min_x))
        miny = float(math.floor(min_y))
        maxx = float(math.floor(max_x))
        maxy = float(math.floor(max_y))
        source_bounds = (minx, miny, maxx, maxy)

        # Buffer coordinates
        buffer_distance_m = 10
        buf_minx = minx - buffer_distance_m
        buf_miny = miny - buffer_distance_m
        buf_maxx = maxx + buffer_distance_m
        buf_maxy = maxy + buffer_distance_m

        ee_rectangle = ee.Geometry.Rectangle(
            [buf_minx, buf_miny, buf_maxx, buf_maxy],
            crs,
            geodesic=False
        )

        rectangle = {"ee_geometry": ee_rectangle, "bounds": source_bounds, "crs": crs}
        return rectangle

    def as_utm_bbox(self):
        """
        Converts bbox to UTM projection
        :return:
        """
        if self.projection_type == ProjectionType.GEOGRAPHIC:
            utm_crs = get_utm_zone_from_latlon_point(self.centroid)
            if self.geo_type == GeoType.CITY:
                geo_extent = construct_city_aoi_json(self.city_id, self.aoi_id)
                bbox = GeoExtent(bbox=geo_extent, crs=utm_crs)
            else:
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
        if self.projection_type == ProjectionType.GEOGRAPHIC:
            return self
        else:
            reproj_bbox = reproject_units(self.min_x, self.min_y, self.max_x, self.max_y, self.crs, WGS_CRS)
            # round to minimize drift
            rounded_box = (reproj_bbox[0], reproj_bbox[1], reproj_bbox[2], reproj_bbox[3])
            bbox = GeoExtent(bbox=rounded_box, crs=WGS_CRS)
            return bbox


# =========== Fishnet ====================================================
MAX_SIDE_LENGTH_METERS = 50000  # This values should cover most situations
MAX_SIDE_LENGTH_DEGREES = 0.5  # Given that for latitude, 50000m * (1deg/111000m)

def _truncate_to_nearest_interval(tile_side_meters, spatial_resolution):
    # Snap the cell increment to the closest whole increment
    floor_increment = math.floor((tile_side_meters / spatial_resolution)) * spatial_resolution
    ceil_increment = math.ceil((tile_side_meters / spatial_resolution)) * spatial_resolution

    floor_offset = abs(floor_increment - tile_side_meters)
    ceil_offset = abs(ceil_increment - tile_side_meters)
    nearest_increment = floor_increment if floor_offset < ceil_offset else ceil_increment

    return nearest_increment


def get_degree_offsets_for_meter_units(bbox: GeoExtent, tile_side_degrees):
    if bbox.projection_type != ProjectionType.GEOGRAPHIC:
        raise ValueError(f"Bbox must have CRS set to {WGS_CRS}")

    mid_x = (bbox.min_x + bbox.max_x) / 2
    x_offset = get_haversine_distance(mid_x, bbox.min_y, mid_x + tile_side_degrees, bbox.min_y)

    mid_y = (bbox.min_y + bbox.max_y) / 2
    y_offset = get_haversine_distance(bbox.min_x, mid_y, bbox.min_x, mid_y + tile_side_degrees)

    return x_offset, y_offset


def _get_offsets(bbox, tile_side_length, tile_buffer_size, length_units, spatial_resolution, output_as):
    if output_as == ProjectionType.GEOGRAPHIC:
        if length_units == "degrees":
            x_tile_side_units = y_tile_side_units = tile_side_length

            tile_buffer_units = tile_buffer_size
        else:  #meters
            raise Exception("Currently does not support length_units in meters and output_as latlon")
    else:  # projected
        if length_units == "degrees":
            x_tile_side_meters, y_tile_side_meters = get_degree_offsets_for_meter_units(bbox, tile_side_length)
            x_tile_side_units = _truncate_to_nearest_interval(x_tile_side_meters, spatial_resolution)
            y_tile_side_units = _truncate_to_nearest_interval(y_tile_side_meters, spatial_resolution)

            avg_side_meters = (x_tile_side_meters + y_tile_side_meters) / 2
            tile_buffer_units = avg_side_meters * (tile_buffer_size / tile_side_length)
        else:  # meters
            tile_side_meters = _truncate_to_nearest_interval(tile_side_length, spatial_resolution)
            x_tile_side_units = y_tile_side_units = tile_side_meters

            tile_buffer_units = tile_buffer_size

    return x_tile_side_units, y_tile_side_units, tile_buffer_units


def _get_bounding_coords(bbox, output_as):
    if output_as == ProjectionType.GEOGRAPHIC:
        if bbox.projection_type == ProjectionType.GEOGRAPHIC:
            start_x_coord, start_y_coord = (bbox.min_x, bbox.min_y)
            end_x_coord, end_y_coord = (bbox.max_x, bbox.max_y)
        else:  #meters
            raise Exception("Currently does not support length_units in meters and output_as latlon")
    else:  # projected
        if bbox.projection_type == ProjectionType.GEOGRAPHIC:
            project_bbox = bbox.as_utm_bbox()
            start_x_coord, start_y_coord = (project_bbox.min_x, project_bbox.min_y)
            end_x_coord, end_y_coord = (project_bbox.max_x, project_bbox.max_y)
        else:  # meters
            start_x_coord, start_y_coord = (bbox.min_x, bbox.min_y)
            end_x_coord, end_y_coord = (bbox.max_x, bbox.max_y)

    return start_x_coord, start_y_coord, end_x_coord, end_y_coord


def _build_tile_geometry(x_coord, y_coord, end_x_coord, end_y_coord, x_tile_side_units, y_tile_side_units, tile_buffer_units):
    cell_min_x = x_coord - tile_buffer_units
    cell_min_y = y_coord - tile_buffer_units

    tile_max_x = x_coord + x_tile_side_units
    cell_max_x = tile_max_x if tile_max_x < end_x_coord else end_x_coord
    cell_max_x = cell_max_x + tile_buffer_units

    tile_max_y = y_coord + y_tile_side_units
    cell_max_y = tile_max_y if tile_max_y < end_y_coord else end_y_coord
    cell_max_y = cell_max_y + tile_buffer_units

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


def create_fishnet_grid(bbox: GeoExtent,
                        tile_side_length: float = 0, tile_buffer_size: float = 0, length_units: str = "meters",
                        spatial_resolution: int = 1,
                        output_as: ProjectionType = ProjectionType.UTM) -> gpd.GeoDataFrame:
    """
    Constructs a grid of tiled areas in either geographic or utm space.
    :param bbox: bounding dimensions of the enclosing box around the grid.
    :param tile_side_length: tile size in specified units. Max is 10000m or approx. 0.1 degrees.
    :param tile_buffer_size: buffer size in specified units.
    :param length_units: units for tile_side_length and tile_buffer_size in either "meters" or "degrees".
    :param spatial_resolution: distance in meters for incremental spacing of the tile size.
    :param output_as: reference system in which the grid is constructed as a ProjectionType.
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
            length_units = "meters"  # a placeholder value

    length_units = length_units.lower()

    valid_length_units = ['degrees', 'meters']
    if length_units not in valid_length_units:
        raise ValueError(f"Invalid length_units ('{length_units}'). "
                         f"Valid methods: [{valid_length_units}]")

    if length_units == "degrees":
        if tile_side_length > MAX_SIDE_LENGTH_DEGREES:
            raise ValueError('Value for tile_side_length is too large.')
    else:
        if tile_side_length > MAX_SIDE_LENGTH_METERS:
            raise ValueError('Value for tile_side_length is too large.')

    x_tile_side_units, y_tile_side_units, tile_buffer_units = \
        _get_offsets(bbox, tile_side_length, tile_buffer_size, length_units, spatial_resolution, output_as)

    start_x_coord, start_y_coord, end_x_coord, end_y_coord = _get_bounding_coords(bbox, output_as)

    # Restrict the cell size to something reasonable. It is best to limit the size to minimize invalid grid
    # definitions and expansion into adjacent UTM zones. As reference, a UTM zone at the equator is ~670,000 m.
    # Assuming 1 km tile size, then 1,000 cells would equal 1,000,000 m grid width - so a 1000 cell limit is
    # somewhat larger than one UTM zone.
    maximum_grid_side_count = 1000
    x_cell_count = math.floor((end_x_coord - start_x_coord) / x_tile_side_units)
    y_cell_count = math.floor((end_y_coord - start_y_coord) / y_tile_side_units)
    if x_cell_count > maximum_grid_side_count:
        raise ValueError('Failure. Grid would have too many cells along the x axis.')
    if y_cell_count > maximum_grid_side_count:
        raise ValueError('Failure. Grid would have too many cells along the y axis.')

    geom_array = []
    x_coord = start_x_coord
    y_coord = start_y_coord
    while y_coord < end_y_coord:
        while x_coord < end_x_coord:
            geom = _build_tile_geometry(x_coord, y_coord, end_x_coord, end_y_coord, x_tile_side_units, y_tile_side_units, tile_buffer_units)
            geom_array.append(geom)
            x_coord += x_tile_side_units
        x_coord = start_x_coord

        y_coord += y_tile_side_units

    if bbox.projection_type == ProjectionType.GEOGRAPHIC and output_as == ProjectionType.GEOGRAPHIC:
        grid_crs = WGS_CRS
    elif bbox.projection_type == ProjectionType.GEOGRAPHIC and output_as == ProjectionType.UTM:
        grid_crs = get_utm_zone_from_latlon_point(bbox.centroid)
    else:
        grid_crs = bbox.crs

    fishnet = gpd.GeoDataFrame(geom_array, columns=["geometry"]).set_crs(grid_crs)
    # Make a copy of the geometry to preserve the full extent of the tile as immutable_fishnet_geometry, since the geometry
    # column is modified in other processing.
    fishnet["immutable_fishnet_geometry"] = fishnet["geometry"]
    return fishnet


# ================= LayerGroupBy ==============
DEFAULT_MAX_TILE_SIZE_M = 15000

class LayerGroupBy:
    def __init__(self, aggregate, geo_zone: GeoZone, spatial_resolution=None, layer=None, custom_tile_size_m=None, masks=[]):
        self.aggregate = aggregate
        self.masks = masks
        self.geo_zone = geo_zone
        self.custom_tile_size_m = custom_tile_size_m
        self.spatial_resolution = spatial_resolution
        self.layer = layer

    def mean(self):
        return self._compute_statistic("mean")

    def count(self):
        return self._compute_statistic("count")

    def sum(self):
        return self._compute_statistic("sum")

    def _compute_statistic(self, stats_func):
        return self._zonal_stats(stats_func, self.geo_zone, self.aggregate, self.layer, self.masks,
                                 self.custom_tile_size_m, self.spatial_resolution)

    @staticmethod
    def _zonal_stats(stats_func, geo_zone, aggregate, layer, masks, custom_tile_size_m, spatial_resolution):
        zones = geo_zone.zones.reset_index(drop=True)
        # Get area of zone in square degrees
        box_area = box(*zones.total_bounds).area

        tile_size_meters = custom_tile_size_m if custom_tile_size_m is not None else DEFAULT_MAX_TILE_SIZE_M

        # if area of zone is within tolerance, then query as a single tile, otherwise sub-tile
        if box_area <= tile_size_meters**2:
            stats = LayerGroupBy._zonal_stats_tile([stats_func], geo_zone, zones, aggregate,
                                                   layer, masks, spatial_resolution)
        else:
            stats = LayerGroupBy._zonal_stats_fishnet(stats_func, geo_zone, zones, aggregate, layer,
                                                      masks, tile_size_meters, spatial_resolution)

        if layer is not None:
            # decode zone and layer value using bit operations
            stats["layer"] = stats["zone"].astype("uint32").values >> 16
            stats["zone"] = stats["zone"].astype("uint32").values & 65535

            # group layer values together into a dictionary per zone
            def group_layer_values(df):
                layer_values = df.drop(columns="zone").groupby("layer").sum()
                layer_dicts = layer_values.to_dict()
                return layer_dicts[stats_func]

            stats = stats.groupby("zone").apply(group_layer_values)

            return stats

        if 'geo_level' in zones.columns:
            result_stats = stats[['zone',stats_func]]
            result_stats = result_stats.rename(columns={stats_func: 'value'})
        else:
            result_stats = stats[stats_func]

        return result_stats


    @staticmethod
    def _zonal_stats_fishnet(stats_func, geo_zone, zones, aggregate, layer, masks, tile_size_m, spatial_resolution):
        # fishnet GeoDataFrame into smaller tiles
        crs = zones.crs.srs

        if crs == WGS_CRS:
            bbox = GeoExtent(bbox=geo_zone, crs=WGS_CRS)
            output_as = ProjectionType.GEOGRAPHIC
        else:
            bbox = GeoExtent(bbox=geo_zone, crs=crs)
            output_as = ProjectionType.UTM

        fishnet = create_fishnet_grid(bbox=bbox, tile_side_length=tile_size_m, length_units="meters",
                                      spatial_resolution=spatial_resolution, output_as=output_as)

        # ------- Use below for testing
        # file = '/tmp/test_result_tif_files/scratch/fishet_grid.geojson'
        # saveable_fishnet = fishnet.drop(columns=['immutable_fishnet_geometry'])
        # saveable_fishnet.to_file(file, driver='GeoJSON')
        # ------- Use above for testing

        # spatial join with fishnet grid and then intersect geometries with fishnet tiles
        # this processing reduces the tile extent to cover the extent needed for the contained zone polygons
        joined = zones.sjoin(fishnet)
        joined["geometry"] = joined.intersection(joined["immutable_fishnet_geometry"])

        # remove linestring artifacts due to float precision
        gdf = joined[joined.geometry.type.isin(['Polygon', 'MultiPolygon'])]

        # separate out zones intersecting to tiles in their own data frames
        tile_gdfs = [
            tile[["index", "geometry"]]
            for _, tile in gdf.groupby("index_right")
        ]
        tile_funcs = LayerGroupBy.get_stats_funcs(stats_func)

        # run zonal stats per tiled data frame
        print(f"Input covers too much area, splitting into {len(tile_gdfs)} tiles")
        tile_stats = pd.concat([
            LayerGroupBy._zonal_stats_tile(tile_funcs,
                                           LayerGroupBy._merge_tile_geometry_into_query_gdf(tile_gdf, zones),
                                           zones, aggregate, layer, masks, spatial_resolution)
            for tile_gdf in tile_gdfs
        ])

        # Aggregate values by zone column
        aggregated = (tile_stats
                      .groupby("zone", as_index=False)
                      .apply(LayerGroupBy._aggregate_stats, stats_func)
                      )

        # Rename column to statistical function
        if None in aggregated.columns:
            aggregated.rename(columns={None: stats_func}, inplace=True)

        return aggregated.reset_index()

    @staticmethod
    def _aggregate_stats(df, stats_func):
        if stats_func == "count":
            return df["count"].sum()
        elif stats_func == "mean":
            # mean must weight by number of pixels used for each tile
            return (df["mean"] * df["count"]).sum() / df["count"].sum()
        elif stats_func == "sum":
            return df["sum"].sum()

    @staticmethod
    def get_stats_funcs(stats_func):
        if stats_func == "mean":
            # mean requires both count and mean to get weighted mean across tiles
            return ["count", "mean"]
        else:
            return [stats_func]

    @staticmethod
    def _merge_tile_geometry_into_query_gdf(tile_gdf, zones):
        query_gdf = zones
        query_gdf.loc[tile_gdf.index, 'geometry'] = tile_gdf['geometry']
        adjusted_gdf = query_gdf[query_gdf.index.isin(tile_gdf.index)]
        return adjusted_gdf

    @staticmethod
    def _zonal_stats_tile(stats_func, tile_gdf, zones, aggregate, layer, masks, spatial_resolution):
        bbox = GeoExtent(tile_gdf)

        aggregate_data = aggregate.retrieve_data(bbox=bbox, s3_bucket=CIF_CACHE_S3_BUCKET_URI, s3_env=DEFAULT_PRODUCTION_ENV,
                                                         spatial_resolution=spatial_resolution)

        if isinstance(aggregate_data, xr.DataArray) and aggregate_data.data.size == 0:
            return None
        else:
            mask_datum = [mask.retrieve_data(bbox=bbox, s3_bucket=CIF_CACHE_S3_BUCKET_URI, s3_env=DEFAULT_PRODUCTION_ENV,
                                                     spatial_resolution=spatial_resolution) for mask in masks]

            if layer is not None:
                layer_data = layer.retrieve_data(bbox=bbox, s3_bucket=CIF_CACHE_S3_BUCKET_URI, s3_env=DEFAULT_PRODUCTION_ENV,
                                                         spatial_resolution=spatial_resolution)
            else:
                layer_data = None

            # align to highest resolution raster, which should be the largest raster
            # since all are clipped to the extent
            raster_data = [data for data in mask_datum + [aggregate_data] + [layer_data] if isinstance(data, xr.DataArray)]
            align_to = sorted(raster_data, key=lambda data: data.size, reverse=True).pop()
            aligned_aggregate_data = LayerGroupBy._align(aggregate_data, align_to)
            aligned_mask_datum = [LayerGroupBy._align(data, align_to) for data in mask_datum]

            if layer is not None:
                aligned_layer_data = LayerGroupBy._align(layer_data, align_to)
            else:
                aligned_layer_data = None

            for mask in aligned_mask_datum:
                aligned_aggregate_data = aligned_aggregate_data.where(~np.isnan(mask))

            # Get zones differently for single or multiple tiles
            if isinstance(tile_gdf, GeoDataFrame):
                tile_gdf = tile_gdf
            else:
                tile_gdf = tile_gdf.zones

            result_stats = None
            if 'geo_level' not in zones.columns:
                result_stats = LayerGroupBy._compute_zonal_stats(stats_func, layer, tile_gdf, align_to, aligned_layer_data,
                                                                 aligned_aggregate_data)
            else:
                geo_levels = zones['geo_level'].unique()
                for index, level in enumerate(geo_levels):
                    level_gdf = tile_gdf[tile_gdf['geo_level'] == level]

                    stats = LayerGroupBy._compute_zonal_stats(stats_func, layer, level_gdf, align_to, aligned_layer_data,
                                                              aligned_aggregate_data)

                    # combine stats from each geo_level
                    if result_stats is None:
                        result_stats = stats
                    else:
                        # if metric values for a prior level are already in the results data, then merge in the new stats,
                        # then combine them into a single column.
                        merged_df = pd.merge(result_stats, stats, on='zone', how='outer')

                        for func in stats_func:
                            func_x_col = f"{func}_x"
                            func_y_col = f"{func}_y"
                            merged_df[func] = merged_df[func_x_col].combine_first(merged_df[func_y_col])

                            merged_df = merged_df.drop(columns=[func_x_col, func_y_col])
                        result_stats = merged_df

            return result_stats

    @staticmethod
    def _compute_zonal_stats(stats_func, layer, tile_gdf, align_to, layer_data, aggregate_data):
        zones = LayerGroupBy._rasterize(tile_gdf, align_to)

        if layer is not None:
            # encode layer into zones by bitshifting
            zones = zones + (layer_data.astype("uint32") << 16)

        stats = zonal_stats(zones, aggregate_data, stats_funcs=stats_func)

        return stats

    @staticmethod
    def _align(data_layer, align_to):
        if isinstance(data_layer, xr.DataArray):
            try:
                return data_layer.rio.reproject_match(align_to).assign_coords({
                    "x": align_to.x,
                    "y": align_to.y,
                })
            except Exception as e_msg:
                raise Exception(f"Unable to align data due to exception: {e_msg}")
        elif isinstance(data_layer, gpd.GeoDataFrame):
            gdf = data_layer.to_crs(align_to.rio.crs).reset_index()
            return LayerGroupBy._rasterize(gdf, align_to)
        else:
            raise NotImplementedError("Can only align DataArray or GeoDataFrame")

    @staticmethod
    def _rasterize(gdf, snap_to: xr.DataArray):
        from shapely.validation import make_valid
        from rasterio.features import rasterize

        gdf['geometry'] = gdf['geometry'].apply(make_valid)
        if gdf.empty:
            nan_array = np.full(snap_to.shape, np.nan, dtype=float)
            raster = snap_to.copy(data=nan_array)
            raster_da = raster.rio.reproject_match(snap_to)
        else:
            crs = snap_to.rio.crs
            reproj_gdf = gdf.to_crs(crs)

            # Extract spatial dimensions and transform from the xarray
            transform = snap_to.rio.transform()
            out_shape = (snap_to.rio.height, snap_to.rio.width)

            # Prepare the geometries and values for rasterization
            shapes = [(geom, value) for geom, value in zip(reproj_gdf.geometry, reproj_gdf.index)]

            # Perform rasterization
            raster1 = rasterize(
                shapes=shapes,
                out_shape=out_shape,
                transform=transform,
                fill=np.nan,  # Fill value for areas outside polygons
                dtype='float32'
            )

            raster_da = xr.DataArray(
                raster1,
                dims=("y", "x"),
                coords={"y": snap_to["y"], "x": snap_to["x"]},
                attrs={"name": "index"}
            ).rio.write_crs(reproj_gdf.crs)

            raster_da = raster_da.rio.reproject_match(snap_to)

        return raster_da


class Layer():
    OUTPUT_FILE_FORMAT = None

    def __init__(self, aggregate=None, masks=[]):
        self.aggregate = aggregate
        if aggregate is None:
            self.aggregate = self

        self.masks = masks

    @abstractmethod
    def get_data(self, bbox: GeoExtent, spatial_resolution: int = None, resampling_method: str = None) -> \
            Union[xr.DataArray, gpd.GeoDataFrame]:
        """
        Extract the data from the source and return it in a way we can compare to other layers.
        :param bbox: a tuple of floats representing the bounding box, (min x, min y, max x, max y)
        :param spatial_resolution: resolution of continuous raster data in meters
        :param resampling_method: interpolation method for continuous raster layers (bilinear, bicubic, nearest)
        :return: A rioxarray-format DataArray or a GeoPandas DataFrame
        """
        ...

    def write(self, bbox: GeoExtent, target_file_path: str,
              tile_side_length: int = None, buffer_size: int = None, length_units: str = None,
              spatial_resolution: int = None, resampling_method: str = None, **kwargs):
        """
        Write the layer to a path. Does not apply masks.
        :param bbox: (min x, min y, max x, max y)
        :param target_file_path: local path to output to
        :param tile_side_length: optional param to tile the results into multiple files specified as tile length on a side
        :param buffer_size: tile buffer distance
        :param length_units: units for tile_side_length and buffer_size (degrees, meters)
        :param spatial_resolution: resolution of continuous raster data in meters
        :param resampling_method: interpolation method for continuous raster layers (bilinear, bicubic, nearest)
        :return:
        """

        if target_file_path is None:
            print("Can't write output to None path")
            return

        file_format = self.OUTPUT_FILE_FORMAT

        if tile_side_length is None:
            utm_geo_extent = bbox.as_utm_bbox()  # currently only support output as utm
            clipped_data = self.aggregate.get_data(bbox=bbox,  spatial_resolution=spatial_resolution,
                                                     resampling_method=resampling_method)

            delete_s3_file_if_exists(target_file_path)
            delete_s3_folder_if_exists(target_file_path)
            write_layer(clipped_data, target_file_path, file_format)
        else:
            tile_grid_gdf = create_fishnet_grid(bbox=bbox, tile_side_length=tile_side_length, tile_buffer_size=0,
                                                length_units=length_units, spatial_resolution=spatial_resolution)
            tile_grid_gdf = Layer._add_tile_name_column(tile_grid_gdf)

            buffered_tile_grid_gdf = None
            if buffer_size and buffer_size > 0:
                buffered_tile_grid_gdf = (
                    create_fishnet_grid(bbox=bbox, tile_side_length=tile_side_length, tile_buffer_size=buffer_size,
                                        length_units=length_units, spatial_resolution=spatial_resolution))
                buffered_tile_grid_gdf = Layer._add_tile_name_column(buffered_tile_grid_gdf)

            # write tile grid to geojson file
            write_tile_grid(tile_grid_gdf, target_file_path, 'tile_grid.geojson')

            # if tiles were buffered, also write unbuffered tile grid to geojson file
            if buffered_tile_grid_gdf is not None and len(buffered_tile_grid_gdf) > 0:
                write_tile_grid(buffered_tile_grid_gdf, target_file_path, 'tile_grid_unbuffered.geojson')

            utm_crs = tile_grid_gdf.crs.srs
            for tile in tile_grid_gdf.itertuples():
                tile_name = tile.tile_name
                tile_bbox = GeoExtent(bbox=tile.geometry.bounds, crs=utm_crs)

                file_path = os.path.join(target_file_path, tile_name)
                layer_data = self.aggregate.get_data(bbox=tile_bbox,  spatial_resolution=spatial_resolution,
                                                     resampling_method=resampling_method)
                write_layer(layer_data, file_path, file_format)


    def cache_city_data(self, bbox: GeoExtent, s3_bucket: str, s3_env: str, spatial_resolution: int = None,
                              force_data_refresh: bool = False):
        """
        Extract the data from the S3 cache otherwise source and return it in a way we can compare to other layers.
        :param city_aoi: specifies a specific AOI for a city extent that does not match the standard city extent
        :param force_data_refresh: specifies whether data files cached in S3 can be used for fulfilling the retrieval.
        """

        if bbox.geo_type != GeoType.CITY:
            raise ValueError("Non-city data cannot be cached.")

        standard_env = standardize_s3_env(s3_env)
        retrieved_cached_data, _, target_uri = retrieve_city_cache(self.aggregate, geo_extent=bbox, s3_bucket=s3_bucket, output_env=standard_env,
                                                                 city_aoi_modifier=None, force_data_refresh=force_data_refresh)

        if retrieved_cached_data is None:
            self._build_city_cache(bbox, spatial_resolution, target_uri)
        else:
            print(f">>>Layer {self.aggregate.__class__.__name__} is already cached ..")


    def retrieve_data(self, bbox: GeoExtent, s3_bucket: str, s3_env: str, city_aoi_modifier: (float, float, float, float)=None,
                              spatial_resolution: int = None) -> Union[
        xr.DataArray, gpd.GeoDataFrame]:
        """
        Extract the data from the S3 cache otherwise source and return it in a way we can compare to other layers.
        :param force_data_refresh: specifies whether data files cached in S3 can be used for fulfilling the retrieval.
        """

        standard_env = standardize_s3_env(s3_env)
        result_data, _, target_uri = retrieve_city_cache(self.aggregate, bbox, s3_bucket=s3_bucket, output_env=standard_env,
                                                         city_aoi_modifier=city_aoi_modifier, force_data_refresh=False)

        if result_data is None:
            if city_aoi_modifier is None:
                query_geoextent = bbox
            else:
                query_geoextent = GeoExtent(bbox=city_aoi_modifier, crs=bbox.crs)

            result_data = self.aggregate.get_data(bbox=query_geoextent, spatial_resolution=spatial_resolution)

            # Opportunistically cache city data
            if bbox.geo_type == GeoType.CITY and city_aoi_modifier is None:
                self._build_city_cache(self, bbox, spatial_resolution, target_uri)

        return result_data


    def _build_city_cache(self, bbox, spatial_resolution, target_uri):
        if bbox.geo_type == GeoType.CITY:
            if hasattr(self.aggregate, 'PROCESSING_TILE_SIDE_M'):
                tile_side_m = self.aggregate.PROCESSING_TILE_SIDE_M
            else:
                tile_side_m = None
            bbox_area = bbox.as_utm_bbox().polygon.area
            if tile_side_m is not None and bbox_area > tile_side_m ** 2 and self.OUTPUT_FILE_FORMAT == GTIFF_FILE_EXTENSION:
                self._cache_data_by_fishnet_tiles(bbox=bbox, tile_side_m=tile_side_m, spatial_resolution=spatial_resolution,
                                                  target_uri=target_uri)
            else:
                result_data = self.aggregate.get_data(bbox=bbox, spatial_resolution=spatial_resolution)
                delete_s3_file_if_exists(target_uri)
                delete_s3_folder_if_exists(target_uri)
                write_layer(result_data, target_uri, self.OUTPUT_FILE_FORMAT)
        else:
            raise ValueError(f"Data not cached for {self.aggregate.__class__.__name__}.  Data can only be cached for CITY geo_extent.")


    def _get_completed_tile_ids(self, file_paths):
        results = []
        for path in file_paths:
            filename = os.path.basename(path)
            id = int(filename.split('_', 1)[1].replace('.tif', ''))
            results.append(id)
        return results


    def _cache_data_by_fishnet_tiles(self, bbox, tile_side_m, spatial_resolution, target_uri):
        # TODO: Code currently only handles raster data
        output_as = ProjectionType.UTM
        utm_box = bbox.as_utm_bbox()
        crs = utm_box.crs

        fishnet = create_fishnet_grid(bbox=utm_box, tile_side_length=tile_side_m, length_units='meters',
                                      spatial_resolution=spatial_resolution, output_as=output_as)

        with tempfile.TemporaryDirectory() as temp_dir:
            # TODO Add verification of complete set of files

            # First, read from source and write to local temp directory
            processed_count = 0
            retry_count = 0
            expected_result_count = len(fishnet)
            uncompleted_tiles = fishnet
            while processed_count < expected_result_count and retry_count < 10:
                tasks = []

                for index, tile in uncompleted_tiles.iterrows():
                    task = dask.delayed(self._process_fishnet_tile)(index, tile, crs, spatial_resolution, temp_dir)
                    tasks.append(task)

                # run them all in parallel with threads
                target_gb = 3
                try:
                    unretrieved_tile_ids = self._run_tasks(tasks, target_gb)
                except Exception as e:
                    print(f"Failed to process a tile fo {target_uri}: {e}. Retrying.")

                missing_tiles = [item for item in unretrieved_tile_ids if not isinstance(item, str)]
                file_paths = self._get_all_tif_file_paths(temp_dir)

                # Note this check only accounts for tiles that were missed due to dask failures and not download errors
                processed_count = len(file_paths) + len(missing_tiles)
                if processed_count == expected_result_count:
                    uncompleted_tiles = gpd.GeoDataFrame(geometry=[])
                else:
                    completed_tile_ids = self._get_completed_tile_ids(file_paths)
                    uncompleted_tiles = fishnet.drop(completed_tile_ids).drop(missing_tiles)

                retry_count +=1

            # Second, write data to target S3 cache
            total_file_bytes = get_folder_size(temp_dir)
            file_paths = self._get_all_tif_file_paths(temp_dir)
            if total_file_bytes <= MAX_RASTER_BYTES_FOR_SINGLE_FILE_OUTPUT:
                # Combine tiles into a single file and write to cache
                import rasterio
                from rasterio.merge import merge
                import os
                try:
                    src_files_to_mosaic = [rasterio.open(fp) for fp in file_paths]
                    mosaic, out_trans = merge(src_files_to_mosaic)

                    # Step 4: Copy metadata and write to new file
                    out_meta = src_files_to_mosaic[0].meta.copy()
                    out_meta.update({
                        "driver": "GTiff",
                        "height": mosaic.shape[1],
                        "width": mosaic.shape[2],
                        "transform": out_trans
                    })

                    temp_file_path = os.path.join(temp_dir, 'composite_layer.tif')
                    with rasterio.open(temp_file_path, "w", **out_meta) as dest:
                        dest.write(mosaic)

                    # write mosaic to cache
                    create_uri_target_folder(target_uri)
                    delete_s3_file_if_exists(target_uri)
                    delete_s3_folder_if_exists(target_uri)
                    self._write_data_to_cache(temp_file_path, target_uri)
                except  Exception as e:
                    raise Exception(f"Failed to process {target_uri}: {e}")
            else:
                # Write individual tiles to cache
                create_uri_target_folder(target_uri)
                delete_s3_file_if_exists(target_uri)
                delete_s3_folder_if_exists(target_uri)

                tile_indices = []
                for file in file_paths:
                    tile = Path(file).stem

                    # extract the index
                    index = int(tile[len('tile_'):])
                    tile_indices.append(index)

                    target_tile_uri = f"{target_uri}/{tile}.{GTIFF_FILE_EXTENSION}"

                    try:
                        self._write_data_to_cache(file, target_tile_uri)
                    except  Exception as e:
                        raise Exception(f"Failed to process {target_tile_uri}: {e}")

                # Write after all other files so file presence can be used as indication of complete data upload
                self._write_grid_index_to_cache(fishnet, tile_indices, target_uri, crs)

    def _write_data_to_cache(self, source_file_path, target_tile_uri):
        if target_tile_uri.startswith('s3://'):
            file_key = get_file_key_from_url(target_tile_uri)
            bucket = get_bucket_name_from_s3_uri(target_tile_uri)

            s3_client.upload_file(
                source_file_path, bucket, file_key, ExtraArgs={"ACL": "public-read"}
            )
        else:
            target_file_path = get_file_path_from_uri(target_tile_uri)
            shutil.move(source_file_path, target_file_path)


    def _write_grid_index_to_cache(self, fishnet, tile_indices, file_uri, crs):
        import json
        json_snippets = []
        for index, tile in fishnet.iterrows():
            if index in tile_indices:
                tile_bounds = tile.geometry.bounds
                tile_file_name = self._construct_tile_name(index)
                tile_uri = f"{file_uri}/{tile_file_name}"
                key = get_key_from_s3_uri(tile_uri)
                tile_row = {
                    "key": key,
                    "bbox": tile_bounds,
                    "crs": crs
                }
                snippet = json.dumps(tile_row)
                json_snippets.append(snippet)

        metadata_file = f"{file_uri}/geotiff_index.json"
        parsed_snippets = [json.loads(snippet) for snippet in json_snippets]
        write_json(parsed_snippets, metadata_file)


    def _run_tasks(self, tasks, target_gb: int):
        import multiprocessing as mp
        import psutil
        from dask import compute

        memory_info = psutil.virtual_memory()
        available_memory = memory_info.available  # Available memory in bytes
        available_memory_gb = available_memory / (1024 ** 3)
        max_workers_by_memory = int(available_memory_gb / target_gb)

        max_workers_by_cpu_availability = int(mp.cpu_count() - 1)

        num_workers = (
            max_workers_by_memory
            if max_workers_by_memory < max_workers_by_cpu_availability
            else max_workers_by_cpu_availability
        )

        memory_limit = f"{target_gb}GB"

        unretrieved_tile_ids = compute(
            *tasks,
            scheduler="threads",
            num_workers=num_workers,
            threads_per_worker=1,
            memory_limit=memory_limit,
        )

        return unretrieved_tile_ids


    def _get_all_tif_file_paths(self, directory):
        tif_files = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.endswith('.tif') and os.path.isfile(os.path.join(directory, f))
        ]
        return tif_files

    def _process_fishnet_tile(self, index, tile, crs, spatial_resolution, temp_dir):
        tile_bounds = tile['geometry'].bounds
        geo_extent = GeoExtent(tile_bounds, crs)

        # buffer the tile bbox so that it can be later cleanly trimmed back to original extent
        buffered_utm_bbox = geo_extent.buffer_utm_bbox(2)

        retry_count = 0
        tile_data = None
        while tile_data is None and retry_count < 3:
            tile_data = self.aggregate.get_data(bbox=buffered_utm_bbox, spatial_resolution=spatial_resolution)
            # pause to avoid over-contention against service
            random_wait = random.randint(2,5)
            time.sleep(random_wait)
            retry_count += 1

        if tile_data is None:
            unretrieved_tile_id = index
        else:
            _, tile_data = standardize_y_dimension_direction(tile_data)

            # clip back to original tile extent
            clipped_tile = extract_tif_subarea(tile_data, geo_extent)

            file_name = self._construct_tile_name(index)
            temp_file_path = os.path.join(temp_dir, file_name)
            write_layer(clipped_tile, temp_file_path, GTIFF_FILE_EXTENSION)

            unretrieved_tile_id = ''

        return unretrieved_tile_id

    def _construct_tile_name(self, tile_index):
        padded_index = str(tile_index).zfill(TILE_NUMBER_PADCOUNT)
        file_name = f'tile_{padded_index}.tif'
        return file_name


    def mask(self, *layers):
        """
        Apply layers as masks
        :param layers: lis
        :return:
        """
        return Layer(aggregate=self, masks=self.masks + list(layers))

    def groupby(self, geo_zone, spatial_resolution=None, layer=None, custom_tile_size_m=None):
        """
        Group layers by zones.
        :param geo_zone: GeoZone containing geometries to group by.
        :param spatial_resolution: resolution of continuous raster layers in meters
        :param layer: Additional categorical layer to group by
        :return: LayerGroupBy object that can be aggregated.
        """
        return LayerGroupBy(self.aggregate, geo_zone, spatial_resolution, layer, custom_tile_size_m, self.masks)


    @staticmethod
    def _add_tile_name_column(tile_grid):
        tile_grid['tile_name'] = (tile_grid.index
                                  .to_series()
                                  .apply(lambda x: f'tile_{str(x + 1).zfill(TILE_NUMBER_PADCOUNT)}'))
        return tile_grid


# ============== Raster Layer handling ================

def validate_raster_resampling_method(resampling_method):
    VALID_RASTER_RESAMPLING_METHODS = ['bilinear', 'bicubic', 'nearest']
    if resampling_method not in VALID_RASTER_RESAMPLING_METHODS:
        raise ValueError(f"Invalid resampling method ('{resampling_method}'). "
                         f"Valid methods: {VALID_RASTER_RESAMPLING_METHODS}")


def set_resampling_for_continuous_raster(image: ee.Image, resampling_method: str,
                                         target_resolution: int, default_resolution: int,
                                         kernel_convolution, crs: str):
    """
    Function sets the resampling method on the GEE query dictionary for use on continuous raster layers.
    GEE only supports bilinear and bicubic interpolation methods.
    :param: kernel_convolution: optional ee.Kernel for smoothing rasters
    """
    validate_raster_resampling_method(resampling_method)

    if target_resolution == default_resolution:
        data = image
    else:
        if resampling_method == 'nearest':
            data = (image
                    .toFloat()  # Ensure values are float in order to successfully use interpolation
                    .reproject(crs=crs, scale=target_resolution)
                    )
        else:
            if kernel_convolution is None:
                data = (image
                        .toFloat()  # Ensure values are float in order to successfully use interpolation
                        .resample(resampling_method)
                        .reproject(crs=crs, scale=target_resolution)
                        )
            else:
                # Convert values to float in order to successfully use interpolation
                data = (image
                        .toFloat()  # Ensure values are float in order to successfully use interpolation
                        .resample(resampling_method)
                        .reproject(crs=crs, scale=target_resolution)
                        .convolve(kernel_convolution)
                        )
    return data


def get_image_collection(
        image_collection: ImageCollection,
        ee_rectangle,
        scale: int,
        name: str = None
) -> xr.DataArray:
    """
    Read an ImageCollection from Google Earth Engine into an xarray DataArray
    :param image_collection: the ee.ImageCollection to read
    :param bbox: the bounding box (min x, min y, max x, max y) to read the data from
    :param name: optional name to print while reporting progress
    :return:
    """
    if scale is None:
        raise Exception("Spatial_resolution cannot be None.")

    # See link regarding bug in crs specification https://github.com/google/Xee/issues/118
    crs = ee_rectangle['crs']
    if crs == WGS_CRS:
        raise Exception("Output in geographic units is currently not supported for raster layers.")

    try:
        ds = xr.open_dataset(
            image_collection,
            engine='ee',
            scale=scale,
            crs=crs,
            geometry=ee_rectangle['ee_geometry'],
            chunks={'X': 512, 'Y': 512},
        )
        with ProgressBar():
            print(f"Extracting layer {name} from Google Earth Engine for bbox :")
            data = ds.compute()
    except Exception as ex_msg:
        raise ValueError(f"GEE download failed with exception: {ex_msg}")

    # get in rioxarray format
    data = data.squeeze("time")
    data = data.transpose("Y", "X").rename({'X': 'x', 'Y': 'y'})

    # remove scale_factor used for NetCDF, this confuses rioxarray GeoTiffs
    for data_var in list(data.data_vars.values()):
        del data_var.encoding["scale_factor"]

    # clip to ee_rectangle
    west, south, east, north = ee_rectangle['bounds']
    longitude_range = slice(west, east)
    latitude_range = slice(south, north)
    clipped_data = data.sel(x=longitude_range, y=latitude_range)

    return clipped_data


class Metric():
    def __init__(self, metric=None):
        self.metric = metric
        if metric is None:
            self.metric = self

    @abstractmethod
    def get_metric(self, geo_zone: GeoZone, spatial_resolution: int) -> Union[pd.Series, pd.DataFrame]:
        """
        Construct polygonal dataset using baser layers
        :return: A rioxarray-format GeoPandas DataFrame
        """
        ...


    def write(self, geo_zone: GeoZone, target_file_path: str = None,
              spatial_resolution: int = None, **kwargs):
        """
        Write the metric to a path. Does not apply masks.
        :param geo_zone: a GeoZone object
        :param target_file_path: local or s3 path to output to
        :param spatial_resolution: resolution of continuous raster data in meters
        :param force_data_refresh: forces layer data to be pulled from source instead of cache
        """
        if target_file_path is None:
            print("Can't write output to None path")
            return

        indicator = self.metric.get_metric(geo_zone, spatial_resolution=spatial_resolution)

        if indicator is None:
            indicator = self._expand_empty_results_to_results_with_null_value(geo_zone)

        Metric._verify_extension(target_file_path, f".{CSV_FILE_EXTENSION}")

        if isinstance(indicator, (float, int)):
            indicator = pd.Series([indicator])

        if isinstance(indicator, Series):
            indicator.name = 'value'

            result_df = geo_zone.zones
            indicator_df = pd.concat([result_df, indicator], axis=1)
        else:
            indicator_df = indicator

        # if 'metric_id' not in indicator_df.columns:
        #     indicator_df = indicator_df.assign(metric_id=feature_id)

        if 'geo_id' in indicator_df.columns:
            indicator_df = _standardize_city_metrics_columns(indicator_df, None)

        if isinstance(indicator_df, gpd.GeoDataFrame):
            indicator_df = indicator_df.drop(columns="geometry")

        write_metric(indicator_df, target_file_path, CSV_FILE_EXTENSION)


    def write_as_geojson(self, geo_zone: GeoZone, target_file_path: str = None,
                         spatial_resolution: int = None, **kwargs):

        """
        Write the metric to a path. Does not apply masks.
        :return:
        """

        if target_file_path is None:
            print("Can't write output to None path")
            return

        indicator = self.metric.get_metric(geo_zone, spatial_resolution=spatial_resolution)

        if indicator is None:
            indicator = self._expand_empty_results_to_results_with_null_value(geo_zone)

        Metric._verify_extension(target_file_path, f".{GEOJSON_FILE_EXTENSION}")

        if isinstance(indicator, (int, float)):
            indicator = pd.Series([indicator])
        if isinstance(indicator, Series):
            indicator.name = 'value'

        result_df = geo_zone.zones
        if isinstance(indicator, pd.DataFrame):
            indicator_df = pd.concat([result_df['geometry'], indicator], axis=1)
        elif not isinstance(indicator, gpd.GeoDataFrame):
            indicator_df = pd.concat([result_df, indicator], axis=1)
        else:
            indicator_df = indicator

        # if 'metric_id' not in indicator_df.columns:
        #     indicator_df = indicator_df.assign(metric_id=feature_id)

        if 'geo_id' in indicator_df.columns:
            indicator_df = _standardize_city_metrics_columns(indicator_df, 'geometry')

        if not isinstance(indicator_df, gpd.GeoDataFrame):
            indicator_gdf = gpd.GeoDataFrame(indicator_df, geometry='geometry')
        else:
            indicator_gdf = indicator_df

        write_metric(indicator_gdf, target_file_path, GEOJSON_FILE_EXTENSION)


    def cache_city_metric(self, geo_zone: GeoZone, s3_bucket: str, s3_env: str, spatial_resolution: int = None,
                          force_data_refresh: bool = False) -> tuple[Union[pd.Series, pd.DataFrame], str]:

        if geo_zone.geo_type != GeoType.CITY:
            raise ValueError("Non-city data cannot be cached.")

        standard_env = standardize_s3_env(s3_env)
        retrieved_cached_data, feature_id, file_uri = retrieve_city_cache(self.metric, geo_zone, s3_bucket, standard_env, None,
                                                                          force_data_refresh)
        if retrieved_cached_data is None:
            result_metric = self.get_metric(geo_zone=geo_zone, spatial_resolution=spatial_resolution)
        else:
            print(f">>>Reading {self.__class__.__name__} metric data from cache..")
            result_metric = retrieved_cached_data

        zones = geo_zone.zones
        if isinstance(result_metric, pd.DataFrame) and 'zone' in result_metric.columns:
            zones['index'] = zones['index'].astype(float)
            result_metric['zone'] = result_metric['zone'].astype(float)
            results_metric_df = pd.merge(zones, result_metric, left_on='index', right_on='zone', how='left')
            if 'metric_id' not in results_metric_df.columns:
                results_metric_df = results_metric_df.assign(metric_id=feature_id)
            result_metric = _standardize_city_metrics_columns(results_metric_df, None)

        if retrieved_cached_data is None and geo_zone.geo_type == GeoType.CITY:
            write_metric(result_metric, file_uri, self.OUTPUT_FILE_FORMAT)

        return result_metric, feature_id


    def retrieve_metric(self, geo_zone: GeoZone, s3_bucket: str, s3_env: str, spatial_resolution: int = None,
                          force_data_refresh: bool = False) -> tuple[Union[pd.Series, pd.DataFrame], str]:

        if geo_zone.geo_type != GeoType.CITY:
            raise ValueError("Non-city data cannot be retrieved.")

        standard_env = standardize_s3_env(s3_env)
        result_metric, feature_id, file_uri = retrieve_city_cache(self.metric, geo_zone, s3_bucket, standard_env, None,
                                                                          force_data_refresh)

        if result_metric is None:
            result_metric = self.get_metric(geo_zone=geo_zone, spatial_resolution=spatial_resolution)

            # Opportunistically cache city metric
            if geo_zone.geo_type == GeoType.CITY:
                write_metric(result_metric, file_uri, self.OUTPUT_FILE_FORMAT)

        return result_metric


    def _expand_empty_results_to_results_with_null_value(self, geo_zone: GeoZone) -> Union[pd.DataFrame, pd.Series]:
        if geo_zone.geo_type == GeoType.CITY:
            admin_count = len(geo_zone.zones)
            padded_rows = pd.Series([''] * admin_count)
        else:
            padded_rows = pd.Series([''] * 1)

        return padded_rows



    @staticmethod
    def _verify_extension(file_path, extension):
        if Path(file_path).suffix != extension:
            raise ValueError(f"File name must have '{extension}' extension")


def _standardize_city_metrics_columns(metrics_df, supplemental_column):
    columns = ['geo_id', 'geo_name', 'geo_level', 'metric_id', 'value']
    if supplemental_column is not None:
        columns.append(supplemental_column)

    result_df = metrics_df[columns]
    return result_df

def _decide_if_write_can_be_skipped(feature, selection_object, output_path, s3_env):  # Determine if write can be skipped
    if output_path is None or len(output_path.strip()) == 0:
        skip_write = True
    elif selection_object.geo_type == GeoType.CITY:
        default_s3_uri, _, _, _ = build_file_key(s3_env, feature, selection_object)
        skip_write = True if default_s3_uri == output_path else False
    else:
        skip_write = False

    return skip_write


def get_class_default_spatial_resolution(obj):
    obj_param_info = get_param_info(obj.get_data)
    obj_spatial_resolution = obj_param_info.get('spatial_resolution')
    return obj_spatial_resolution


def get_param_info(func):
    import inspect
    signature = inspect.signature(func)
    default_values = {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }
    return default_values


def standardize_s3_env(output_env):
    standard_env = DEFAULT_PRODUCTION_ENV if output_env is None else output_env.lower()
    if standard_env not in (DEFAULT_PRODUCTION_ENV, DEFAULT_DEVELOPMENT_ENV):
        raise ValueError(f"Invalid output environment ({output_env}) for Layer")
    else:
        return standard_env


def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            if os.path.isfile(file_path):  # Ensure it's a file
                total_size += os.path.getsize(file_path)
    return total_size

def string_to_float_list(s, delimiter=","):
    # Remove square brackets and whitespace
    s_clean = s.strip().strip("[]")

    # Split by delimiter and clean each element
    elements = [x.strip() for x in s_clean.split(delimiter)]

    # Convert to int (or float if needed)
    return [float(x) for x in elements if x]
