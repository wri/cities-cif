import os
from abc import abstractmethod
from typing import Union, Tuple
from uuid import uuid4
from osgeo import gdal

import ee
import boto3
import math
from dask.diagnostics import ProgressBar
from ee import ImageCollection
from geocube.api.core import make_geocube
from shapely.geometry import box, polygon
from xrspatial import zonal_stats
import geopandas as gpd
import xarray as xr
import numpy as np
import utm
import shapely.geometry as geometry
import pandas as pd

MAX_TILE_SIZE_DEGREES = 0.5 # TODO Why was this value selected?

class Layer:
    def __init__(self, aggregate=None, masks=[]):
        self.aggregate = aggregate
        if aggregate is None:
            self.aggregate = self

        self.masks = masks

    @abstractmethod
    def get_data(self, bbox: Tuple[float]) -> Union[xr.DataArray, gpd.GeoDataFrame]:
        """
        Extract the data from the source and return it in a way we can compare to other layers.
        :param bbox: a tuple of floats representing the bounding box, (min x, min y, max x, max y)
        :return: A rioxarray-format DataArray or a GeoPandas DataFrame
        """
        ...

    def mask(self, *layers):
        """
        Apply layers as masks
        :param layers: lis
        :return:
        """
        return Layer(aggregate=self, masks=self.masks + list(layers))

    def groupby(self, zones, layer=None):
        """
        Group layers by zones.
        :param zones: GeoDataFrame containing geometries to group by.
        :param layer: Additional categorical layer to group by
        :return: LayerGroupBy object that can be aggregated.
        """
        return LayerGroupBy(self.aggregate, zones, layer, self.masks)

    def write(self, bbox, output_path, tile_degrees=None, buffer_size=None, **kwargs):
        """
        Write the layer to a path. Does not apply masks.

        :param bbox: (min x, min y, max x, max y)
        :param output_path: local or s3 path to output to
        :param tile_degrees: optional param to tile the results into multiple files specified as tile length on a side
        :param buffer_size: tile buffer distance
        :return:
        """

        if tile_degrees is None:
            clipped_data = self.aggregate.get_data(bbox)
            write_layer(output_path, clipped_data)
        else:
            tile_grid, unbuffered_tile_grid = _get_tile_boundaries(bbox, tile_degrees, buffer_size)

            # write raster data to files
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            for tile in tile_grid:
                tile_name = tile['tile_name']
                tile_geom = tile['geometry']

                file_path = os.path.join(output_path, tile_name)
                clipped_data = self.aggregate.get_data(tile_geom.bounds)
                write_layer(file_path, clipped_data)

            # write tile grid to geojson file
            _write_tile_grid(tile_grid, output_path, 'tile_grid.geojson')

            # if tiles were buffered, also write unbuffered tile grid to geojson file
            if unbuffered_tile_grid:
                _write_tile_grid(unbuffered_tile_grid, output_path, 'tile_grid_unbuffered.geojson')


def _get_tile_boundaries(bbox, tile_degrees, buffer_size):
    has_buffer = True if buffer_size is not None and buffer_size != 0 else False
    if has_buffer:
        tiles = create_fishnet_grid(*bbox, tile_degrees, buffer_size)
        unbuffered_tiles = create_fishnet_grid(*bbox, tile_degrees)
    else:
        tiles = create_fishnet_grid(*bbox, tile_degrees)
        unbuffered_tiles = None

    tile_grid = []
    unbuffered_tile_grid = []
    for index in range(0, len(tiles)):
        tile_serial_id = index + 1
        tile_suffix = str(tile_serial_id).zfill(3)
        tile_name = f'tile_{tile_suffix}.tif'

        tile_geom = tiles.iloc[index]['geometry']
        tile_grid.append({"tile_name": tile_name, "geometry": tile_geom})

        if has_buffer:
            unbuffered_tile_geom = unbuffered_tiles.iloc[index]['geometry']
            unbuffered_tile_grid.append({"tile_name": tile_name, "geometry": unbuffered_tile_geom})

    return tile_grid, unbuffered_tile_grid

def _write_tile_grid(tile_grid, output_path, target_file_name):
    tile_grid = gpd.GeoDataFrame(tile_grid, crs='EPSG:4326')
    tile_grid_file_path = str(os.path.join(output_path, target_file_name))
    tile_grid.to_file(tile_grid_file_path)

class LayerGroupBy:
    def __init__(self, aggregate, zones, layer=None, masks=[]):
        self.aggregate = aggregate
        self.masks = masks
        self.zones = zones.reset_index()
        self.layer = layer

    def mean(self):
        return self._zonal_stats("mean")

    def count(self):
        return self._zonal_stats("count")

    def _zonal_stats(self, stats_func):
        if box(*self.zones.total_bounds).area <= MAX_TILE_SIZE_DEGREES**2:
            stats = self._zonal_stats_tile(self.zones, [stats_func])
        else:
            stats = self._zonal_stats_fishnet(stats_func)

        if self.layer is not None:
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

        return stats[stats_func]

    def _zonal_stats_fishnet(self, stats_func):
        # fishnet GeoDataFrame into smaller tiles
        fishnet = create_fishnet_grid(*self.zones.total_bounds, MAX_TILE_SIZE_DEGREES)

        # spatial join with fishnet grid and then intersect geometries with fishnet tiles
        joined = self.zones.sjoin(fishnet)
        joined["geometry"] = joined.intersection(joined["fishnet_geometry"])

        # remove linestring artifacts due to float precision
        gdf = joined[joined.geometry.type.isin(['Polygon', 'MultiPolygon'])]

        # separate out zones intersecting to tiles in their own data frames
        tile_gdfs = [
            tile[["index", "geometry"]]
            for _, tile in gdf.groupby("index_right")
        ]
        tile_funcs = get_stats_funcs(stats_func)

        # run zonal stats per data frame
        print(f"Input covers too much area, splitting into {len(tile_gdfs)} tiles")
        tile_stats = pd.concat([
            self._zonal_stats_tile(tile_gdf, tile_funcs)
            for tile_gdf in tile_gdfs
        ])

        aggregated = tile_stats.groupby("zone").apply(_aggregate_stats, stats_func)
        aggregated.name = stats_func

        return aggregated.reset_index()

    def _zonal_stats_tile(self, tile_gdf, stats_func):
        bbox = tile_gdf.total_bounds
        aggregate_data = self.aggregate.get_data(bbox)
        mask_datum = [mask.get_data(bbox) for mask in self.masks]
        layer_data = self.layer.get_data(bbox) if self.layer is not None else None

        # align to highest resolution raster, which should be the largest raster
        # since all are clipped to the extent
        raster_data = [data for data in mask_datum + [aggregate_data] + [layer_data] if isinstance(data, xr.DataArray)]
        align_to = sorted(raster_data, key=lambda data: data.size, reverse=True).pop()
        aggregate_data = self._align(aggregate_data, align_to)
        mask_datum = [self._align(data, align_to) for data in mask_datum]

        if self.layer is not None:
            layer_data = self._align(layer_data, align_to)

        for mask in mask_datum:
            aggregate_data = aggregate_data.where(~np.isnan(mask))

        zones = self._rasterize(tile_gdf, align_to)

        if self.layer is not None:
            # encode layer into zones by bitshifting
            zones = zones + (layer_data.astype("uint32") << 16)

        stats = zonal_stats(zones, aggregate_data, stats_funcs=stats_func)

        return stats

    def _align(self, layer, align_to):
        if isinstance(layer, xr.DataArray):
            return layer.rio.reproject_match(align_to).assign_coords({
                "x": align_to.x,
                "y": align_to.y,
            })
        elif isinstance(layer, gpd.GeoDataFrame):
            gdf = layer.to_crs(align_to.rio.crs).reset_index()
            return self._rasterize(gdf, align_to)
        else:
            raise NotImplementedError("Can only align DataArray or GeoDataFrame")

    def _rasterize(self, gdf, snap_to):
        raster = make_geocube(
            vector_data=gdf,
            measurements=["index"],
            like=snap_to,
        ).index

        return raster.rio.reproject_match(snap_to)


def get_utm_zone_epsg(bbox) -> str:
    """
    Get the UTM zone projection for given a bounding box.

    :param bbox: tuple of (min x, min y, max x, max y)
    :return: the EPSG code for the UTM zone of the centroid of the bbox
    """
    centroid = box(*bbox).centroid
    utm_x, utm_y, band, zone = utm.from_latlon(centroid.y, centroid.x)

    if centroid.y > 0:  # Northern zone
        epsg = 32600 + band
    else:
        epsg = 32700 + band

    return f"EPSG:{epsg}"


def create_fishnet_grid(min_lon, min_lat, max_lon, max_lat, cell_size, buffer_size=0, tile_units_in_degrees=True):
    lon_coord, lat_coord = (min_lon, min_lat)
    geom_array = []

    if tile_units_in_degrees:
        if cell_size > 0.5:
            raise Exception('Value for cell_size must be < 0.5 degrees.')

        lon_side_offset = cell_size
        lat_side_offset = cell_size
        lon_buffer_offset = buffer_size
        lat_buffer_offset = buffer_size
    else:
        if cell_size < 10:
            raise Exception('Value for cell_size must be >= 10 meters.')

        center_lat = (min_lat + max_lat) / 2
        lon_side_offset, lat_side_offset = offset_meters_to_geographic_degrees(center_lat, cell_size)
        if buffer_size == 0:
            lon_buffer_offset = 0
            lat_buffer_offset = 0
        else:
            lon_buffer_offset, lat_buffer_offset = offset_meters_to_geographic_degrees(center_lat, buffer_size)

    # Polygon Size
    while lat_coord < max_lat:
        while lon_coord < max_lon:
            cell_min_lon = lon_coord - lon_buffer_offset
            cell_min_lat = lat_coord - lat_buffer_offset
            cell_max_lon = lon_coord + lon_side_offset + lon_buffer_offset
            cell_max_lat = lat_coord + lat_side_offset + lat_buffer_offset
            geom = geometry.Polygon(
                [
                    (cell_min_lon, cell_min_lat),
                    (cell_min_lon, cell_max_lat),
                    (cell_max_lon, cell_max_lat),
                    (cell_max_lon, cell_min_lat),
                    (cell_min_lon, cell_min_lat),
                ]
            )
            geom_array.append(geom)
            lon_coord += lon_side_offset
        lon_coord = min_lon

        lat_coord += lat_side_offset

    fishnet = gpd.GeoDataFrame(geom_array, columns=["geometry"]).set_crs("EPSG:4326")
    fishnet["fishnet_geometry"] = fishnet["geometry"]
    return fishnet


def _aggregate_stats(df, stats_func):
    if stats_func == "count":
        return df["count"].sum()
    elif stats_func == "mean":
        # mean must weight by number of pixels used for each tile
        return (df["mean"] * df["count"]).sum() / df["count"].sum()


def get_stats_funcs(stats_func):
    if stats_func == "mean":
        # mean requires both count and mean to get weighted mean across tiles
        return ["count", "mean"]
    else:
        return [stats_func]


def get_image_collection(
        image_collection: ImageCollection,
        bbox: Tuple[float],
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

    crs = get_utm_zone_epsg(bbox)

    # See link regarding bug in crs specification https://github.com/google/Xee/issues/118
    ds = xr.open_dataset(
        image_collection,
        engine='ee',
        scale=scale,
        crs=crs,
        geometry=ee.Geometry.Rectangle(*bbox),
        chunks={'X': 512, 'Y': 512},
    )

    with ProgressBar():
        print(f"Extracting layer {name} from Google Earth Engine for bbox {bbox}:")
        data = ds.compute()

    # get in rioxarray format
    data = data.squeeze("time").transpose("Y", "X").rename({'X': 'x', 'Y': 'y'})

    # remove scale_factor used for NetCDF, this confuses rioxarray GeoTiffs
    for data_var in list(data.data_vars.values()):
        del data_var.encoding["scale_factor"]

    return data

def write_layer(path, data):
    if isinstance(data, xr.DataArray):
        write_dataarray(path, data)
    elif isinstance(data, gpd.GeoDataFrame):
        data.to_file(path, driver="GeoJSON")
    else:
        raise NotImplementedError("Can only write DataArray, Dataset, or GeoDataFrame")

def write_dataarray(path, data):
    # for rasters, need to write to locally first then copy to cloud storage
    if path.startswith("s3://"):
        tmp_path = f"{uuid4()}.tif"
        data.rio.to_raster(raster_path=tmp_path, driver="COG")

        s3 = boto3.client('s3')
        s3.upload_file(tmp_path, path.split('/')[2], '/'.join(path.split('/')[3:]))

        os.remove(tmp_path)
    else:
        data.rio.to_raster(raster_path=path, driver="COG")

def offset_meters_to_geographic_degrees(decimal_latitude, length_m):
    # TODO consider replacing this spherical calculation with ellipsoidal
    earth_radius_m = 6378137
    rad = 180/math.pi

    lon_degree_offset = abs((length_m / (earth_radius_m * math.cos(math.pi*decimal_latitude/180))) * rad)
    lat_degree_offset = abs((length_m / earth_radius_m) * rad)

    return lon_degree_offset, lat_degree_offset