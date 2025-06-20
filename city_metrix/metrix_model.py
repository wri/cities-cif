import math
import os
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
from shapely import geometry
from shapely.geometry import box
from xrspatial import zonal_stats


from city_metrix.constants import WGS_CRS, ProjectionType, GeoType, GEOJSON_FILE_EXTENSION, CSV_FILE_EXTENSION, \
    DEFAULT_PRODUCTION_ENV, DEFAULT_DEVELOPMENT_ENV, DEFAULT_STAGING_ENV
from city_metrix.metrix_dao import (write_tile_grid, write_layer, write_metric,
                                    get_city, get_city_admin_boundaries, get_city_boundary)
from city_metrix.metrix_tools import (get_projection_type, get_haversine_distance, get_utm_zone_from_latlon_point,
                                      reproject_units, parse_city_aoi_json, construct_city_aoi_json, buffer_bbox)
from city_metrix.cache_manager import retrieve_cached_city_data, build_file_key


# ============= GeoZone ======================================
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
            city_id, aoi_id = parse_city_aoi_json(city_json)
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


def _build_buffered_aoi_from_city_boundaries(city_id, admin_level):
    # Construct bbox from total bounds of all admin levels
    # increase the AOI by a small amount to avoid edge issues
    boundaries = get_city_admin_boundaries(city_id, admin_level)
    if len(boundaries) == 1:
        west, south, east, north = boundaries.bounds
    else:
        west, south, east, north = boundaries.total_bounds

    buffer_meters = 2
    bbox = buffer_bbox(west, south, east, north , buffer_meters)

    return bbox


class GeoExtent():
    def __init__(self, bbox:Union[tuple[float, float, float, float]|GeoZone|str], crs=WGS_CRS):
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
        else:
            if isinstance(bbox, GeoZone):
                city_json = construct_city_aoi_json(bbox.city_id, "city_admin_level")
            else:
                city_json = bbox
            city_id, aoi_id = parse_city_aoi_json(city_json)
            city = get_city(city_id)
            admin_level = city.get(aoi_id, None)
            if not admin_level:
                raise ValueError(f"City metadata for {self.city_id} does not have geometry for admin_level: 'city_admin_level'")
            bbox = _build_buffered_aoi_from_city_boundaries(city_id, admin_level)
            self.city_id = city_id
            self.aoi_id = aoi_id
            self.admin_level = admin_level
            if get_projection_type(crs) == ProjectionType.GEOGRAPHIC:
                self.bbox = bbox
            else:
                reproj_bbox = reproject_units(bbox[1], bbox[0], bbox[3], bbox[2], WGS_CRS, crs)
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
            if self.geo_type == GeoType.CITY:
                geo_extent = construct_city_aoi_json(self.city_id, self.aoi_id)
                bbox = GeoExtent(bbox=geo_extent, crs=WGS_CRS)
            else:
                reproj_bbox = reproject_units(self.min_x, self.min_y, self.max_x, self.max_y, self.crs, WGS_CRS)
                # round to minimize drift
                rounded_box = (reproj_bbox[0], reproj_bbox[1], reproj_bbox[2], reproj_bbox[3])
                bbox = GeoExtent(bbox=rounded_box, crs=WGS_CRS)
            return bbox



# =========== Fishnet ====================================================
MAX_SIDE_LENGTH_METERS = 50000 # This values should cover most situations
MAX_SIDE_LENGTH_DEGREES = 0.5 # Given that for latitude, 50000m * (1deg/111000m)

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
    if output_as==ProjectionType.GEOGRAPHIC:
        if length_units == "degrees":
            x_tile_side_units = y_tile_side_units = tile_side_length

            tile_buffer_units = tile_buffer_size
        else: #meters
            raise Exception("Currently does not support length_units in meters and output_as latlon")
    else: # projected
        if length_units=="degrees":
            x_tile_side_meters, y_tile_side_meters = get_degree_offsets_for_meter_units(bbox, tile_side_length)
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
    if output_as == ProjectionType.GEOGRAPHIC:
        if bbox.projection_type == ProjectionType.GEOGRAPHIC:
            start_x_coord, start_y_coord = (bbox.min_x, bbox.min_y)
            end_x_coord, end_y_coord = (bbox.max_x, bbox.max_y)
        else: #meters
            raise Exception("Currently does not support length_units in meters and output_as latlon")
    else: # projected
        if bbox.projection_type == ProjectionType.GEOGRAPHIC:
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

def create_fishnet_grid(bbox:GeoExtent,
                        tile_side_length:float=0, tile_buffer_size:float=0, length_units:str="meters",
                        spatial_resolution:int=1, output_as:ProjectionType=ProjectionType.UTM) -> gpd.GeoDataFrame:
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
            length_units = "meters" # a placeholder value

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

    if bbox.projection_type == ProjectionType.GEOGRAPHIC and output_as == ProjectionType.GEOGRAPHIC:
        grid_crs = WGS_CRS
    elif bbox.projection_type == ProjectionType.GEOGRAPHIC and output_as== ProjectionType.UTM:
        grid_crs = get_utm_zone_from_latlon_point(bbox.centroid)
    else:
        grid_crs = bbox.crs

    fishnet = gpd.GeoDataFrame(geom_array, columns=["geometry"]).set_crs(grid_crs)
    fishnet["fishnet_geometry"] = fishnet["geometry"]
    return fishnet


# ================= LayerGroupBy ==============
MAX_TILE_SIZE_DEGREES = 0.5 # TODO How was this value selected?

class LayerGroupBy:
    def __init__(self, aggregate, geo_zone: GeoZone, spatial_resolution=None, layer=None, force_data_refresh=True, masks=[]):
        self.aggregate = aggregate
        self.masks = masks
        self.geo_zone = geo_zone
        self.spatial_resolution = spatial_resolution
        self.layer = layer
        self.force_data_refresh = force_data_refresh

    def mean(self):
        return self._compute_statistic("mean")

    def count(self):
        return self._compute_statistic("count")

    def sum(self):
        return self._compute_statistic("sum")

    def _compute_statistic(self, stats_func):
        return self._zonal_stats(stats_func, self.geo_zone, self.aggregate, self.layer, self.masks,
                                 self.spatial_resolution, self.force_data_refresh)

    @staticmethod
    def _zonal_stats(stats_func, geo_zone, aggregate, layer, masks, spatial_resolution, force_data_refresh):
        zones = geo_zone.zones.reset_index(drop=True)
        # Get area of zone in square degrees
        if zones.crs == WGS_CRS:
            box_area = box(*zones.total_bounds).area
        else:
            bounds = zones.total_bounds
            minx, miny, maxx, maxy = reproject_units(bounds[0], bounds[1], bounds[2], bounds[3], zones.crs, WGS_CRS)
            box_area = box(minx, miny, maxx, maxy).area

        # if area of zone is within tolerance, then query as a single tile, otherwise sub-tile
        if box_area <= MAX_TILE_SIZE_DEGREES**2:
            stats = LayerGroupBy._zonal_stats_tile([stats_func], geo_zone, zones, aggregate,
                                                   layer, masks, spatial_resolution, force_data_refresh)
        else:
            stats = LayerGroupBy._zonal_stats_fishnet(stats_func, zones, aggregate, layer,
                                                      masks, spatial_resolution)

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

        result_series = stats[stats_func]

        return result_series

    @staticmethod
    def _zonal_stats_fishnet(stats_func, zones, aggregate, layer, masks, spatial_resolution):
        # fishnet GeoDataFrame into smaller tiles
        crs = zones.crs.srs
        bounds = zones.total_bounds
        if crs == WGS_CRS:
            bbox = GeoExtent(bbox=tuple(bounds), crs=WGS_CRS)
            output_as = ProjectionType.GEOGRAPHIC
        else:
            bbox = GeoExtent(bbox=tuple(bounds), crs=crs)
            output_as = ProjectionType.UTM
        fishnet = create_fishnet_grid(bbox, tile_side_length=MAX_TILE_SIZE_DEGREES, length_units="degrees",
                                      spatial_resolution=spatial_resolution, output_as=output_as)

        # spatial join with fishnet grid and then intersect geometries with fishnet tiles
        joined = zones.sjoin(fishnet)
        joined["geometry"] = joined.intersection(joined["fishnet_geometry"])

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
                                           zones, aggregate, layer, masks, spatial_resolution, False)
            for tile_gdf in tile_gdfs
        ])

        aggregated = (tile_stats
                      .groupby("zone")
                      .apply(LayerGroupBy._aggregate_stats, stats_func, include_groups=False))
        aggregated.name = stats_func

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
    def _zonal_stats_tile(stats_func, geo_zone, zones, aggregate, layer, masks, spatial_resolution, force_data_refresh):
        bbox = GeoExtent(geo_zone)

        aggregate_data = aggregate.get_data_with_caching(bbox=bbox, s3_env=DEFAULT_PRODUCTION_ENV, spatial_resolution=spatial_resolution,
                                                         force_data_refresh = force_data_refresh)
        mask_datum = [mask.get_data_with_caching(bbox=bbox, s3_env=DEFAULT_PRODUCTION_ENV, spatial_resolution=spatial_resolution,
                                    force_data_refresh= force_data_refresh) for mask in masks]
        layer_data = layer.get_data_with_caching(bbox=bbox, s3_env=DEFAULT_PRODUCTION_ENV, spatial_resolution=spatial_resolution,
                                         force_data_refresh= force_data_refresh) if layer is not None else None

        # align to highest resolution raster, which should be the largest raster
        # since all are clipped to the extent
        raster_data = [data for data in mask_datum + [aggregate_data] + [layer_data] if isinstance(data, xr.DataArray)]
        align_to = sorted(raster_data, key=lambda data: data.size, reverse=True).pop()
        aggregate_data = LayerGroupBy._align(aggregate_data, align_to)
        mask_datum = [LayerGroupBy._align(data, align_to) for data in mask_datum]

        if layer is not None:
            layer_data = LayerGroupBy._align(layer_data, align_to)

        for mask in mask_datum:
            aggregate_data = aggregate_data.where(~np.isnan(mask))

        # Get zones differently for single or multiple tiles
        if isinstance(geo_zone, GeoDataFrame):
            tile_gdf = geo_zone
        else:
            tile_gdf = geo_zone.zones

        result_stats = None
        if 'geo_level' not in zones.columns:
            result_stats = LayerGroupBy._compute_zonal_stats(stats_func, layer, tile_gdf, align_to, layer_data, aggregate_data)
        else:
            geo_levels = zones['geo_level'].unique()
            for index, level in enumerate(geo_levels):
                level_gdf = tile_gdf[tile_gdf['geo_level'] == level]

                stats = LayerGroupBy._compute_zonal_stats(stats_func, layer, level_gdf, align_to, layer_data, aggregate_data)

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
            return data_layer.rio.reproject_match(align_to).assign_coords({
                "x": align_to.x,
                "y": align_to.y,
            })
        elif isinstance(data_layer, gpd.GeoDataFrame):
            gdf = data_layer.to_crs(align_to.rio.crs).reset_index()
            return LayerGroupBy._rasterize(gdf, align_to)
        else:
            raise NotImplementedError("Can only align DataArray or GeoDataFrame")

    @staticmethod
    def _rasterize(gdf, snap_to):
        from shapely.validation import make_valid
        gdf['geometry'] = gdf['geometry'].apply(make_valid)
        if gdf.empty:
            nan_array = np.full(snap_to.shape, np.nan, dtype=float)
            raster = snap_to.copy(data=nan_array)
        else:
            raster = make_geocube(
                vector_data=gdf,
                measurements=["index"],
                like=snap_to,
            ).index

        return raster.rio.reproject_match(snap_to)


class Layer():
    OUTPUT_FILE_FORMAT = None
    def __init__(self, aggregate=None, masks=[]):
        self.aggregate = aggregate
        if aggregate is None:
            self.aggregate = self

        self.masks = masks

    @abstractmethod
    def get_data(self, bbox: GeoExtent, spatial_resolution:int=None, resampling_method:str=None) ->\
            Union[xr.DataArray, gpd.GeoDataFrame]:
        """
        Extract the data from the source and return it in a way we can compare to other layers.
        :param bbox: a tuple of floats representing the bounding box, (min x, min y, max x, max y)
        :param spatial_resolution: resolution of continuous raster data in meters
        :param resampling_method: interpolation method for continuous raster layers (bilinear, bicubic, nearest)
        :param force_data_refresh: specifies whether data files cached in S3 can be used for fulfilling the retrieval.
        :return: A rioxarray-format DataArray or a GeoPandas DataFrame
        """
        ...

    def get_data_with_caching(self, bbox: GeoExtent, s3_env:str, spatial_resolution:int=None,
                              force_data_refresh:bool=False) -> Union[xr.DataArray, gpd.GeoDataFrame]:

        standard_env = standardize_s3_env(self, s3_env)
        retrieved_cached_data, _, file_uri = retrieve_cached_city_data(self.aggregate, bbox, standard_env, force_data_refresh)
        result_data = None
        if retrieved_cached_data is None:
            result_data = self.aggregate.get_data(bbox=bbox, spatial_resolution=spatial_resolution)

            # Write to cache
            if bbox.geo_type == GeoType.CITY:
                write_layer(result_data, file_uri, self.OUTPUT_FILE_FORMAT)
        else:
            result_data = retrieved_cached_data

        return result_data

    def mask(self, *layers):
        """
        Apply layers as masks
        :param layers: lis
        :return:
        """
        return Layer(aggregate=self, masks=self.masks + list(layers))

    def groupby(self, geo_zone, spatial_resolution=None, layer=None, force_data_refresh=False):
        """
        Group layers by zones.
        :param geo_zone: GeoZone containing geometries to group by.
        :param spatial_resolution: resolution of continuous raster layers in meters
        :param layer: Additional categorical layer to group by
        :return: LayerGroupBy object that can be aggregated.
        """
        return LayerGroupBy(self.aggregate, geo_zone, spatial_resolution, layer, force_data_refresh, self.masks)


    def write(self, bbox: GeoExtent, s3_env:str, output_uri:str=None,
              tile_side_length:int=None, buffer_size:int=None, length_units:str=None,
              spatial_resolution:int=None, resampling_method:str=None,
              force_data_refresh:bool=False, **kwargs):
        """
        Write the layer to a path. Does not apply masks.
        :param bbox: (min x, min y, max x, max y)
        :param output_uri: local or s3 path to output to
        :param s3_env: name of storage environment (dev, prd)
        :param tile_side_length: optional param to tile the results into multiple files specified as tile length on a side
        :param buffer_size: tile buffer distance
        :param length_units: units for tile_side_length and buffer_size (degrees, meters)
        :param spatial_resolution: resolution of continuous raster data in meters
        :param resampling_method: interpolation method for continuous raster layers (bilinear, bicubic, nearest)
        :param force_data_refresh: forces layer data to be pulled from source instead of cache
        :return:
        """

        standard_env = standardize_s3_env(self, s3_env)
        file_format = self.OUTPUT_FILE_FORMAT

        if tile_side_length is None:
            utm_geo_extent = bbox.as_utm_bbox() # currently only support output as utm
            clipped_data = self.aggregate.get_data_with_caching(bbox=utm_geo_extent, s3_env=standard_env,
                                                                spatial_resolution=spatial_resolution,
                                                                force_data_refresh=force_data_refresh)

            # Determine if write can be skipped
            skip_write = decide_if_write_can_be_skipped(self.aggregate, bbox, output_uri, standard_env)
            if not skip_write:
                write_layer(clipped_data, output_uri, file_format)
        else:
            tile_grid_gdf = create_fishnet_grid(bbox, tile_side_length=tile_side_length, tile_buffer_size=0,
                                            length_units=length_units, spatial_resolution=spatial_resolution)
            tile_grid_gdf = Layer._add_tile_name_column(tile_grid_gdf)

            buffered_tile_grid_gdf = None
            if buffer_size and buffer_size > 0:
                buffered_tile_grid_gdf = (
                    create_fishnet_grid(bbox, tile_side_length=tile_side_length, tile_buffer_size=buffer_size,
                                        length_units=length_units, spatial_resolution=spatial_resolution))
                buffered_tile_grid_gdf = Layer._add_tile_name_column(buffered_tile_grid_gdf)

            # write tile grid to geojson file
            write_tile_grid(tile_grid_gdf, output_uri, 'tile_grid.geojson')

            # if tiles were buffered, also write unbuffered tile grid to geojson file
            if buffered_tile_grid_gdf is not None and len(buffered_tile_grid_gdf) > 0:
                write_tile_grid(buffered_tile_grid_gdf, output_uri, 'tile_grid_unbuffered.geojson')

            utm_crs = tile_grid_gdf.crs.srs
            for tile in tile_grid_gdf.itertuples():
                tile_name = tile.tile_name
                tile_bbox = GeoExtent(bbox=tile.geometry.bounds, crs=utm_crs)

                file_path = os.path.join(output_uri, tile_name)
                layer_data = self.aggregate.get_data(bbox=tile_bbox, spatial_resolution=spatial_resolution,
                                                     resampling_method=resampling_method)
                write_layer(layer_data, file_path, file_format)

    @staticmethod
    def _add_tile_name_column(tile_grid):
        tile_grid['tile_name'] = (tile_grid.index
                                  .to_series()
                                  .apply(lambda x: f'tile_{str(x + 1).zfill(3)}.tif'))
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
                        .toFloat() # Ensure values are float in order to successfully use interpolation
                        .resample(resampling_method)
                        .reproject(crs=crs, scale=target_resolution)
                        )
            else:
                # Convert values to float in order to successfully use interpolation
                data = (image
                        .toFloat() # Ensure values are float in order to successfully use interpolation
                        .resample(resampling_method)
                        .reproject(crs=crs, scale=target_resolution)
                        .convolve(kernel_convolution)
                        )
    return data

def get_image_collection(
        image_collection: ImageCollection,
        ee_rectangle,
        scale: int,
        name: str=None
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

    # get in rioxarray format
    data = data.squeeze("time")
    data = data.transpose("Y", "X").rename({'X': 'x', 'Y': 'y'})

    # remove scale_factor used for NetCDF, this confuses rioxarray GeoTiffs
    for data_var in list(data.data_vars.values()):
        del data_var.encoding["scale_factor"]

    # clip to ee_rectangle
    west, south, east, north  = ee_rectangle['bounds']
    longitude_range = slice(west,east)
    latitude_range = slice(south, north)
    clipped_data = data.sel(x=longitude_range, y=latitude_range)

    return clipped_data


class Metric():
    def __init__(self, metric=None):
        self.metric = metric
        if metric is None:
            self.metric = self

    @abstractmethod
    def get_metric(self, geo_zone: GeoZone, spatial_resolution:int) -> pd.Series:
        """
        Construct polygonal dataset using baser layers
        :return: A rioxarray-format GeoPandas DataFrame
        """
        ...

    def get_metric_with_caching(self, geo_zone: GeoZone, s3_env:str, spatial_resolution:int=None,
                                force_data_refresh:bool=False) -> [Union[xr.DataArray, gpd.GeoDataFrame],str]:

        standard_env = standardize_s3_env(self, s3_env)
        retrieved_cached_data, feature_id, file_uri = retrieve_cached_city_data(self.metric, geo_zone, standard_env, force_data_refresh)
        result_metric = None
        if retrieved_cached_data is None:
            result_metric = self.metric.get_metric(geo_zone=geo_zone, spatial_resolution=spatial_resolution)

            if geo_zone.geo_type == GeoType.CITY:
                write_metric(result_metric, file_uri, self.OUTPUT_FILE_FORMAT)
        else:
            result_metric = retrieved_cached_data.squeeze()

        return result_metric, feature_id

    def write(self, geo_zone: GeoZone, s3_env: str, output_uri:str=None,
              spatial_resolution:int = None, force_data_refresh:bool = False, **kwargs):
        """
        Write the metric to a path. Does not apply masks.
        :param geo_zone: a GeoZone object
        :param output_uri: local or s3 path to output to
        :param s3_env: name of storage environment (dev, staging, prd)
        :param spatial_resolution: resolution of continuous raster data in meters
        :param force_data_refresh: forces layer data to be pulled from source instead of cache
        """
        standard_env = standardize_s3_env(self, s3_env)

        indicator, feature_id = self.metric.get_metric_with_caching(geo_zone, standard_env,
                                                                    spatial_resolution, force_data_refresh)

        if indicator is None:
            raise NotImplementedError("Data not available for this geo_zone.")

        # Determine if write can be skipped
        skip_write = decide_if_write_can_be_skipped(self.metric, geo_zone, output_uri, standard_env)

        if not skip_write:
            Metric._verify_extension(output_uri, f".{CSV_FILE_EXTENSION}")
            indicator.name = 'value'

            result_df = geo_zone.zones
            if 'geo_id' in result_df.columns:
                result_df = result_df[['geo_id', 'geo_name', 'geo_level']]

            if 'geometry' in result_df.columns:
                result_df.drop(columns=['geometry'], inplace=True)

            result_df = result_df.assign(metric_id=feature_id)

            indicator_df = pd.concat([result_df, indicator], axis=1)

            write_metric(indicator_df, output_uri, CSV_FILE_EXTENSION)

    def write_as_geojson(self, geo_zone: GeoZone, s3_env:str, output_uri:str=None,
                         spatial_resolution:int = None, force_data_refresh:bool = False, **kwargs):

        """
        Write the metric to a path. Does not apply masks.
        :return:
        """
        standard_env = standardize_s3_env(self, s3_env)

        indicator, feature_id = self.metric.get_metric_with_caching(geo_zone, standard_env,
                                                                    spatial_resolution, force_data_refresh)

        if indicator is None:
            raise NotImplementedError("Data not available for this geo_zone.")

        # Determine if write can be skipped
        skip_write = decide_if_write_can_be_skipped(self.metric, geo_zone, output_uri, standard_env)

        if not skip_write:
            Metric._verify_extension(output_uri, f".{GEOJSON_FILE_EXTENSION}")
            indicator.name = 'value'

            result_df = geo_zone.zones
            if 'geo_id' in result_df.columns:
                result_df = result_df[['geo_id', 'geo_name', 'geo_level', 'geometry']]

            result_df = result_df.assign(metric_id=feature_id)

            indicator_df = pd.concat([result_df, indicator], axis=1)
            write_metric(indicator_df, output_uri, GEOJSON_FILE_EXTENSION)

    @staticmethod
    def _verify_extension(file_path, extension):
        if Path(file_path).suffix != extension:
            raise ValueError(f"File name must have '{extension}' extension")


def decide_if_write_can_be_skipped(feature, selection_object, output_path, s3_env):       # Determine if write can be skipped
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

def standardize_s3_env(obj, output_env):
    if isinstance(obj, Layer):
        standard_env = DEFAULT_PRODUCTION_ENV if output_env is None else output_env.lower()
        if standard_env not in (DEFAULT_PRODUCTION_ENV, DEFAULT_DEVELOPMENT_ENV):
            raise ValueError(f"Invalid output environment ({output_env}) for Layer")
        else:
            return standard_env
    else:
        standard_env = DEFAULT_STAGING_ENV if output_env is None else output_env.lower()
        if standard_env != DEFAULT_STAGING_ENV:
            raise ValueError(f"Invalid output environment ({output_env}) for Metric")
        else:
            return standard_env