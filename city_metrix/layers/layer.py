from abc import abstractmethod

from geocube.api.core import make_geocube
from xrspatial import zonal_stats
import numpy as np


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

    def groupby(self, zones):
        return LayerGroupBy(self.aggregate, zones, self.masks)


class LayerGroupBy:
    def __init__(self, aggregate, groupby, masks=[]):
        self.aggregate = aggregate
        self.masks = masks
        self.groupby = groupby.reset_index()

    def mean(self, column_name=None):
        return self._zonal_stats("mean", column_name)

    def count(self, column_name=None):
        return self._zonal_stats("count", column_name)

    def _zonal_stats(self, stats_func, column_name=None):
        bbox = self.groupby.total_bounds
        aggregate_data = self.aggregate.get_data(bbox)
        mask_datum = [mask.get_data(bbox) for mask in self.masks]

        # align to highest resolution raster, which should be the largest raster
        # since all are clipped to the extent
        align_to = sorted(mask_datum + [aggregate_data], key=lambda data: data.size, reverse=True).pop()
        aggregate_data = self._align(aggregate_data, align_to)
        mask_datum = [self._align(data, align_to) for data in mask_datum]

        for mask in mask_datum:
            aggregate_data = aggregate_data.where(~np.isnan(mask))

        zones = self._rasterize(self.groupby, align_to)

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





