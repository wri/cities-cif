import fiona
from enum import Enum
import geopandas as gpd
from shapely.geometry import box

from geocube.api.core import make_geocube


class SupportedCity(Enum):
    ARG_Buenos_Aires = "ARG-Buenos_Aires"
    IDN_Jakarta = "IDN-Jakarta"


class City:
    def __init__(self, city: SupportedCity, admin_level: int):
        boundary_uri = f"s3://cities-indicators/data/boundaries/boundary-{city.value}-ADM{admin_level}"
        self.city = city
        self.admin_level = admin_level

        try:
            self.boundaries = gpd.read_file(f"{boundary_uri}.geojson").reset_index()
            self.boundaries_union = gpd.read_file(f"{boundary_uri}union.geojson").reset_index()
            self.bounds = list(self.boundaries_union.total_bounds)
            self.bounding_box = box(*self.bounds)
        except fiona.errors.DriverError as e:
            raise Exception(f"Unable to read boundary files for city {city.value}/{admin_level}:\n {e}")

    def to_raster(self, resolution):
        """
        Rasterize the admin boundaries to the specified resolution.
        :param resolution: resolution in geographic coordinates of the output raster
        :return:
        """

        return make_geocube(
            vector_data=self.boundaries,
            measurements=["index"],
            resolution=(-resolution, resolution),
            geom=self.bounding_box
        ).index