from abc import abstractmethod
from typing import Union, Tuple, List

import ee
from dask.diagnostics import ProgressBar
from ee import ImageCollection
from geocube.api.core import make_geocube
from shapely.geometry import box
from xrspatial import zonal_stats
import geopandas as gpd
import xarray as xr
import numpy as np
import utm
import shapely.geometry as geometry
import pandas as pd


MAX_TILE_SIZE = 0.5


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
        if box(*self.zones.total_bounds).area <= MAX_TILE_SIZE**2:
            return self._zonal_stats_tile(self.zones, [stats_func])[stats_func]
        else:
            return self._zonal_stats_fishnet(stats_func)

    def _zonal_stats_fishnet(self, stats_func):
        # fishnet GeoDataFrame into smaller tiles
        fishnet = create_fishnet_grid(*self.zones.total_bounds, MAX_TILE_SIZE)

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
        tile_stats = pd.concat([
            self._zonal_stats_tile(tile_gdf, tile_funcs)
            for tile_gdf in tile_gdfs
        ])

        aggregated = tile_stats.groupby("zone").apply(_aggregate_stats, stats_func)

        return aggregated

    def _zonal_stats_tile(self, tile_gdf, stats_func):
        bbox = tile_gdf.total_bounds
        aggregate_data = self.aggregate.get_data(bbox)
        mask_datum = [mask.get_data(bbox) for mask in self.masks]

        # align to highest resolution raster, which should be the largest raster
        # since all are clipped to the extent
        raster_data = [data for data in mask_datum + [aggregate_data] if isinstance(data, xr.DataArray)]
        align_to = sorted(raster_data, key=lambda data: data.size, reverse=True).pop()
        aggregate_data = self._align(aggregate_data, align_to)
        mask_datum = [self._align(data, align_to) for data in mask_datum]

        for mask in mask_datum:
            aggregate_data = aggregate_data.where(~np.isnan(mask))

        zones = self._rasterize(tile_gdf, align_to)
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


def create_fishnet_grid(min_x, min_y, max_x, max_y, cell_size):
    x, y = (min_x, min_y)
    geom_array = []

    # Polygon Size
    while y < max_y:
        while x < max_x:
            geom = geometry.Polygon(
                [
                    (x, y),
                    (x, y + cell_size),
                    (x + cell_size, y + cell_size),
                    (x + cell_size, y),
                    (x, y),
                ]
            )
            geom_array.append(geom)
            x += cell_size
        x = min_x
        y += cell_size

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

    crs = get_utm_zone_epsg(bbox)

    ds = xr.open_dataset(
        image_collection,
        engine='ee',
        scale=scale,
        crs=crs,
        geometry=ee.Geometry.Rectangle(*bbox),
        chunks={'X': 512, 'Y': 512},
    )

    with ProgressBar():
        print(f"Extracting layer {name} from Google Earth Engine:")
        data = ds.compute()

    # get in rioxarray format
    data = data.squeeze("time").transpose("Y", "X").rename({'X': 'x', 'Y': 'y'})
    return data

