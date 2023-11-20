from abc import abstractmethod

from geocube.api.core import make_geocube
from xrspatial import zonal_stats


class Layer:
    def __init__(self, masks=[], groupby=None):
        self.masks = masks
        self.groupby = groupby

    @abstractmethod
    def get_data(self):
        ...

    def mask(self, *layers):
        return Layer(masks=self.masks + layers, groupby=self.groupby)

    def groupby(self, groupby):
        # asset geodatafraame
        return Layer(masks=self.masks, groupby=groupby)

    def mean(self, column_name=None):
        return self._zonal_stats("mean")

    def _zonal_stats(self, stats_func, column_name=None):
        if self.groupby is None:
            raise ValueError("Must specify a groupby parameter before running statistics function.")

        bbox = self._get_bbox()  # get bbox
        #grid_xarray = self._get_grid_xarray(bbox)

        data = self.get_data()
        mask_datum = [_snap(mask.get_data(), data) for mask in mask]
        masked_data = reduce(data.where(mask_datum))

        data = self.data.where(reprojected)
        zones = _rasterize(self.groupby)

        stats = zonal_stats(zones=zones, values=masked_data, stats_funcs=[stats_func])
        return self.groupby.reset_index().join(stats).rename({"mean": column_name})

    def _snap(self):
        reprojected = to_reproject.data.rio.reproject_match(reprojecter).assign_coords({
            "x": reprojecter.x,
            "y": reprojecter.y,
        })

    def _rasterize(self, data):
        geoms_with_index = geometries.reset_index()

        self.zones = make_geocube(
            vector_data=geoms_with_index,
            measurements=["index"],
            like=data,
            geom=geoms_with_index.total_bounds
        ).index





