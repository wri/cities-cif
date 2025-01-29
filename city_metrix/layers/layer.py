import math
import os
from abc import abstractmethod
from typing import Union, Tuple
from uuid import uuid4
import shapely.geometry as geometry
import shapely
import utm

import xee
# This osgeo import is essential for proper functioning. Do not remove.
from osgeo import gdal

import ee
import boto3
from dask.diagnostics import ProgressBar
from ee import ImageCollection
from geocube.api.core import make_geocube
from shapely.geometry import box
from xrspatial import zonal_stats
import geopandas as gpd
import xarray as xr
import numpy as np
import pandas as pd

WGS_CRS = 'EPSG:4326'

MAX_TILE_SIZE_DEGREES = 0.5 # TODO Why was this value selected?


class GeoExtent():
    def __init__(self, bbox: tuple[float, float, float, float], crs:str=WGS_CRS):
        self.bbox = bbox

        self.crs = crs
        self.epsg_code = int(self.crs.split(':')[1])
        self.projection_name = get_projection_name(crs)
        self.units = "degrees" if self.projection_name == 'geographic' else "meters"

        self.min_x = bbox[0]
        self.min_y = bbox[1]
        self.max_x = bbox[2]
        self.max_y = bbox[3]

        self.coords = (self.min_x, self.min_y, self.max_x, self.max_y)

        self.centroid = box(self.min_x, self.min_y, self.max_x, self.max_y).centroid

        self.polygon = shapely.box(self.min_x, self.min_y, self.max_x, self.max_y)


    def to_ee_rectangle(self):
        """
        Converts bbox to an Earth Engine geometry rectangle
        """
        if self.projection_name == 'geographic':
            utm_bbox = self.as_utm_bbox()
            minx, miny, maxx, maxy = utm_bbox.bbox
            ee_rectangle = _build_ee_rectangle(round(minx,2), round(miny,2),
                                            round(maxx,2), round(maxy,2),
                                            utm_bbox.crs)
            return ee_rectangle
        elif self.projection_name == 'utm':
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
        if self.projection_name == 'geographic':
            utm_crs = get_utm_zone_from_latlon_point(self.centroid)
            reproj_bbox = reproject_units(self.min_y, self.min_x, self.max_y, self.max_x, WGS_CRS, utm_crs)
            # round to minimize drift
            utm_box = (round(reproj_bbox[1],2), round(reproj_bbox[0],2), round(reproj_bbox[3],2), round(reproj_bbox[2],2))
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
            box = (round(reproj_bbox[0],7), round(reproj_bbox[1],7), round(reproj_bbox[2],7), round(reproj_bbox[3],7))
            bbox = GeoExtent(bbox=box, crs=WGS_CRS)
            return bbox


class Layer():
    def __init__(self, aggregate=None, masks=[]):
        self.aggregate = aggregate
        if aggregate is None:
            self.aggregate = self

        self.masks = masks


    @abstractmethod
    def get_data(self, bbox: GeoExtent, spatial_resolution:int, resampling_method:str) -> Union[xr.DataArray, gpd.GeoDataFrame]:
        """
        Extract the data from the source and return it in a way we can compare to other layers.
        :param bbox: a tuple of floats representing the bounding box, (min x, min y, max x, max y)
        :param spatial_resolution: resolution of continuous raster data in meters
        :param resampling_method: interpolation method for continuous raster layers (bilinear, bicubic, nearest)
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

    def groupby(self, zones, spatial_resolution=None, layer=None):
        """
        Group layers by zones.
        :param zones: GeoDataFrame containing geometries to group by.
        :param spatial_resolution: resolution of continuous raster layers in meters
        :param layer: Additional categorical layer to group by
        :return: LayerGroupBy object that can be aggregated.
        """
        return LayerGroupBy(self.aggregate, zones, spatial_resolution, layer, self.masks)


    def write(self, bbox: GeoExtent, output_path:str,
              tile_side_length:int=None, buffer_size:int=None, length_units:str=None,
              spatial_resolution:int=None, resampling_method:int=None, **kwargs):
        """
        Write the layer to a path. Does not apply masks.
        :param bbox: (min x, min y, max x, max y)
        :param output_path: local or s3 path to output to
        :param tile_side_length: optional param to tile the results into multiple files specified as tile length on a side
        :param buffer_size: tile buffer distance
        :param length_units: units for tile_side_length and buffer_size (degrees, meters)
        :param spatial_resolution: resolution of continuous raster data in meters
        :param resampling_method: interpolation method for continuous raster layers (bilinear, bicubic, nearest)
        :return:
        """

        if tile_side_length is None:
            utm_bbox = bbox.as_utm_bbox() # currently only support output as utm
            clipped_data = self.aggregate.get_data(utm_bbox, spatial_resolution=spatial_resolution,
                                                   resampling_method=resampling_method)
            _write_layer(output_path, clipped_data)
        else:
            tile_grid_gdf = create_fishnet_grid(bbox, tile_side_length=tile_side_length, tile_buffer_size=0,
                                            length_units=length_units, spatial_resolution=spatial_resolution)
            tile_grid_gdf = _add_tile_name_column(tile_grid_gdf)

            buffered_tile_grid_gdf = None
            if buffer_size and buffer_size > 0:
                buffered_tile_grid_gdf = (
                    create_fishnet_grid(bbox, tile_side_length=tile_side_length, tile_buffer_size=buffer_size,
                                        length_units=length_units, spatial_resolution=spatial_resolution))
                buffered_tile_grid_gdf = _add_tile_name_column(buffered_tile_grid_gdf)

            # write raster data to files
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            # write tile grid to geojson file
            _write_tile_grid(tile_grid_gdf, output_path, 'tile_grid.geojson')

            # if tiles were buffered, also write unbuffered tile grid to geojson file
            if buffered_tile_grid_gdf is not None and len(buffered_tile_grid_gdf) > 0:
                _write_tile_grid(buffered_tile_grid_gdf, output_path, 'tile_grid_unbuffered.geojson')

            utm_crs = tile_grid_gdf.crs.srs
            for tile in tile_grid_gdf.itertuples():
                tile_name = tile.tile_name
                tile_bbox = GeoExtent(bbox=tile.geometry.bounds, crs=utm_crs)

                file_path = os.path.join(output_path, tile_name)
                layer_data = self.aggregate.get_data(bbox=tile_bbox, spatial_resolution=spatial_resolution,
                                                     resampling_method=resampling_method)
                _write_layer(file_path, layer_data)


def _add_tile_name_column(tile_grid):
    tile_grid['tile_name'] = (tile_grid.index
                              .to_series()
                              .apply(lambda x: f'tile_{str(x + 1).zfill(3)}.tif'))
    return tile_grid


class LayerGroupBy:
    def __init__(self, aggregate, zones, spatial_resolution=None, layer=None, masks=[]):
        self.aggregate = aggregate
        self.masks = masks
        self.zones = zones.reset_index(drop=True)
        self.spatial_resolution = spatial_resolution
        self.layer = layer

    def mean(self):
        return self._zonal_stats("mean")

    def count(self):
        return self._zonal_stats("count")

    def sum(self):
        return self._zonal_stats("sum")

    def _zonal_stats(self, stats_func):
        if self.zones.crs == WGS_CRS:
            box_area = box(*self.zones.total_bounds).area
        else:
            bounds = self.zones.total_bounds
            minx, miny, maxx, maxy = reproject_units(bounds[0], bounds[1], bounds[2], bounds[3], self.zones.crs, WGS_CRS)
            box_area = box(minx, miny, maxx, maxy).area

        if box_area <= MAX_TILE_SIZE_DEGREES**2:
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
        crs = self.zones.crs.srs
        bounds = self.zones.total_bounds
        if crs == WGS_CRS:
            bbox = GeoExtent(bbox=tuple(bounds), crs=WGS_CRS)
            output_as = 'geographic'
        else:
            bbox = GeoExtent(bbox=tuple(bounds), crs=crs)
            output_as = "utm"
        fishnet = create_fishnet_grid(bbox, tile_side_length=MAX_TILE_SIZE_DEGREES, length_units="degrees",
                                      spatial_resolution=self.spatial_resolution, output_as=output_as)

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
        crs = tile_gdf.crs.srs
        raw_bbox = tile_gdf.total_bounds
        if crs == WGS_CRS:
            bbox = GeoExtent(bbox=tuple(raw_bbox), crs=WGS_CRS)
        else:
            bbox = GeoExtent(bbox=tuple(raw_bbox), crs=crs)
        aggregate_data = self.aggregate.get_data(bbox=bbox, spatial_resolution=self.spatial_resolution)
        mask_datum = [mask.get_data(bbox=bbox, spatial_resolution=self.spatial_resolution) for mask in self.masks]
        layer_data = self.layer.get_data(bbox=bbox, spatial_resolution=self.spatial_resolution) if self.layer is not None else None

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


def _aggregate_stats(df, stats_func):
    if stats_func == "count":
        return df["count"].sum()
    elif stats_func == "mean":
        # mean must weight by number of pixels used for each tile
        return (df["mean"] * df["count"]).sum() / df["count"].sum()
    elif stats_func == "sum":
        return df["sum"].sum()


def get_stats_funcs(stats_func):
    if stats_func == "mean":
        # mean requires both count and mean to get weighted mean across tiles
        return ["count", "mean"]
    else:
        return [stats_func]

VALID_RASTER_RESAMPLING_METHODS = ['bilinear', 'bicubic', 'nearest']

def validate_raster_resampling_method(resampling_method):
    if resampling_method not in VALID_RASTER_RESAMPLING_METHODS:
        raise ValueError(f"Invalid resampling method ('{resampling_method}'). "
                         f"Valid methods: {VALID_RASTER_RESAMPLING_METHODS}")


def set_resampling_for_continuous_raster(image: ee.Image, resampling_method: str, resolution: int,
                                         crs: str):
    """
    Function sets the resampling method on the GEE query dictionary for use on continuous raster layers.
    GEE only supports bilinear and bicubic interpolation methods.
    """
    validate_raster_resampling_method(resampling_method)

    if resampling_method == 'nearest':
        data = (image
                .reproject(crs=crs, scale=resolution))
    else:
        data = (image
                .resample(resampling_method)
                .reproject(crs=crs, scale=resolution))

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

    return data

def _write_layer(path, data):
    if isinstance(data, xr.DataArray):
        was_reversed, data_array = standardize_y_dimension_direction(data)
        _write_dataarray(path, data_array)
    elif isinstance(data, xr.Dataset):
        raise NotImplementedError("Data as Dataset not currently supported")
    elif isinstance(data, gpd.GeoDataFrame):
        data.to_file(path, driver="GeoJSON")
    else:
        raise NotImplementedError("Can only write DataArray or GeoDataFrame")


def _write_dataarray(path, data):
    # for rasters, need to write to locally first then copy to cloud storage
    if path.startswith("s3://"):
        tmp_path = f"{uuid4()}.tif"
        data.rio.to_raster(raster_path=tmp_path, driver="COG")

        s3 = boto3.client('s3')
        s3.upload_file(tmp_path, path.split('/')[2], '/'.join(path.split('/')[3:]))

        os.remove(tmp_path)
    else:
        data.rio.to_raster(raster_path=path, driver="COG")


def _write_tile_grid(tile_grid, output_path, target_file_name):
    tile_grid_file_path = str(os.path.join(output_path, target_file_name))
    tg = tile_grid.drop(columns='fishnet_geometry', axis=1)
    tg.to_file(tile_grid_file_path)

def standardize_y_dimension_direction(data_array):
    was_reversed= False
    y_dimensions = data_array.shape[0]
    if data_array.y.data[0] < data_array.y.data[y_dimensions - 1]:
        data_array = data_array.isel({data_array.rio.y_dim: slice(None, None, -1)})
        was_reversed = True
    return was_reversed, data_array


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


def create_fishnet_grid(bbox:GeoExtent,
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

    valid_output = ['utm', 'geographic']
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
    floor_increment = (tile_side_meters // spatial_resolution) * spatial_resolution
    ceil_increment = -(-tile_side_meters // spatial_resolution) * spatial_resolution
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

    mid_x = (bbox.min_x + bbox.min_x) / 2
    x_offset = get_haversine_distance(mid_x, bbox.min_y, mid_x + tile_side_degrees, bbox.min_y)

    mid_y = (bbox.min_y + bbox.min_y) / 2
    y_offset = get_haversine_distance(bbox.min_x, mid_y, bbox.min_x, mid_y + tile_side_degrees)

    return x_offset, y_offset


def get_projection_name(crs: Union[str|int]):
    if isinstance(crs, str):
        if not crs.startswith('EPSG:'):
            raise Exception("Valid crs string must be specified in form of ('EPSG:n') where n is an EPSG code.")
        epsg_code = int(crs.split(':')[1])
    elif isinstance(crs, int):
        epsg_code = crs
    else:
        raise ValueError(f"Value of ({crs}) is an invalid crs string or epsg code. ")

    if epsg_code == 4326:
        projection_name = 'geographic'
    elif 32601 <= epsg_code <= 32660 or 32701 <= epsg_code <= 32760:
        projection_name = 'utm'
    else:
        raise ValueError(f"CRS ({crs}) not supported.")

    return projection_name

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

def _build_ee_rectangle(min_x, min_y, max_x, max_y, crs):
    ee_rectangle = ee.Geometry.Rectangle(
        [min_x, min_y, max_x, max_y],
        crs,
        geodesic=False
    )
    rectangle = {"ee_geometry": ee_rectangle, "crs": crs}
    return rectangle


