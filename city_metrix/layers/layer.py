from abc import abstractmethod

from geocube.api.core import make_geocube
from shapely.geometry import box
from xrspatial import zonal_stats
import numpy as np
import utm


class Layer:
    def __init__(self, aggregate=None, masks=[]):
        self.aggregate = aggregate
        if aggregate is None:
            self.aggregate = self

        self.masks = masks

    @abstractmethod
    def get_data(self):
        ...

    def mask(self, *layers):
        return Layer(aggregate=self, masks=self.masks + list(layers))

    def groupby(self, zones, layer=None):
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
        bbox = self.zones.total_bounds
        aggregate_data = self.aggregate.get_data(bbox)
        mask_datum = [mask.get_data(bbox) for mask in self.masks]

        # align to highest resolution raster, which should be the largest raster
        # since all are clipped to the extent
        align_to = sorted(mask_datum + [aggregate_data], key=lambda data: data.size, reverse=True).pop()
        aggregate_data = self._align(aggregate_data, align_to)
        mask_datum = [self._align(data, align_to) for data in mask_datum]

        for mask in mask_datum:
            aggregate_data = aggregate_data.where(~np.isnan(mask))

        if self.layer is not None:
            layer_data = self.layer.get_data(bbox)
            aggregate_data = self._align(aggregate_data, layer_data)
            zones = self._rasterize(self.zones, layer_data)
            zones = zones + (layer_data >> 16)

            stats = zonal_stats(zones=zones, values=aggregate_data, stats_funcs=[stats_func])
            stats['layer'] = stats['zone'] << 16
            stats['zone'] = (stats['zones'] >> 16) << 16
            stats = stats.set_index('layer')
        else:
            zones = self._rasterize(self.zones, align_to)
            stats = zonal_stats(zones=zones, values=aggregate_data, stats_funcs=[stats_func])

        return stats[stats_func]

    def _align(self, to_reproject, reprojecter):
        return to_reproject.rio.reproject_match(reprojecter).assign_coords({
            "x": reprojecter.x,
            "y": reprojecter.y,
        })

    def _rasterize(self, zones, snap_to):
        zones_raster = make_geocube(
            vector_data=zones,
            measurements=["index"],
            like=snap_to,
            geom=zones.total_bounds
        ).index

        return zones_raster


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
