import rioxarray

from cities_indicators.city import City
from cities_indicators.layers.raster_layer import RasterLayer


class TropicalTreeCover(RasterLayer):
    S3_PREFIX = "s3://tropical_tree_cover/2020"

    def get_layer_uri(self, city: City):
        file_name = f"{city.country.capitalize().strip()}.tif"
        return f"{self.S3_PREFIX}/{file_name}"



