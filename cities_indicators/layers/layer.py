from geocube.api.core import make_geocube
from xrspatial import zonal_stats


class Layer:
    def __init__(self, data):
        self.data = data

    def filter(self, filter_layer):
        reprojected = filter_layer.data.rio.reproject_match(self.data).assign_coords({
            "x": self.data.x,
            "y": self.data.y,
        })

        data = self.data.where(reprojected)
        return Layer(data)

    def groupby(self, geometries):
        return LayerGroupBy(geometries, self.data)


class LayerGroupBy:
    def __init__(self, geometries, data, output_path=None):
        self.geometries = geometries
        self.data = data

        geoms_with_index = geometries.reset_index()

        self.zones = make_geocube(
            vector_data=geoms_with_index,
            measurements=["index"],
            like=self.data,
            geom=geoms_with_index.total_bounds
        ).index

    def count(self):
        return self._zonal_stats("count")

    def mean(self):
        return self._zonal_stats("mean")

    def _zonal_stats(self, stats_func):
        return zonal_stats(zones=self.zones, values=self.data, stats_funcs=[stats_func])