import functools

from geocube.api.core import make_geocube


class City:
    def __init__(self, boundaries, resolution, country):
        self.extent = boundaries.bbox
        self.boundaries = boundaries
        self.country: str = country

    @functools.lru_cache(maxsize=3, typed=False)
    def to_raster(self, resolution):
        """
        Rasterize the admin boundaries to the specified resolution.
        :param resolution: resolution in geographic coordinates of the output raster
        :return:
        """
        return make_geocube(
            vector_data=self.boundaries,
            measurements="index",
            resolution=(-resolution, resolution),
            geom=self.extent
        )