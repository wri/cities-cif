import rioxarray

from cities_indicators.city import City
from cities_indicators.io import read_vrt, read_gee


class TropicalTreeCover:
    VRT_URI = "s3://cities-indicators/data/tree_cover/tree_mosaic_land/tropical_tree_cover.vrt"
    NO_DATA_VALUE = 255
    TML = "projects/wri-datalab/TML"

    def read(self, city: City, resolution: int):
        data = read_vrt(city, self.VRT_URI, resolution)
        return data.where(data != self.NO_DATA_VALUE)

    def read_from_gee(self, city: City):
        data  = read_gee(city, self.TML)
        return data
