import rioxarray

from cities_indicators.city import City
from cities_indicators.io import read_vrt, read_gee


class TropicalTreeCover:
    VRT_URI = "/Users/jt/Downloads/java-ttc.tiff"  #"s3://cities-indicators/data/tree_cover/tree_mosaic_land/tropical_tree_cover.vrt"
    NO_DATA_VALUE = -99
    TML = "projects/wri-datalab/TropicalTreeCover"

    def read(self, city: City, snap_to=None):
        data = read_vrt(city, self.VRT_URI, snap_to, no_data=self.NO_DATA_VALUE)
        return data

    def read_from_gee(self, city: City):
        data = read_gee(city, self.TML)
        return data
