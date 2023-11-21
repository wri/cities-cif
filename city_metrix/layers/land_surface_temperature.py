import odc.stac
import pystac_client

from .landsat_collection_2 import LandsatCollection2
from .layer import Layer


class LandSurfaceTemperature(Layer):
    def __init__(self, start_date="2013-01-01", end_date="2023-01-01", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def get_data(self, bbox):
        landsat = LandsatCollection2(
            bands=["lwir11"],
            start_date=self.start_date,
            end_date=self.end_date
        ).get_data(bbox)

        celsius_lst = (((landsat.lwir11 * 0.00341802) + 149) - 273.15)
        data = celsius_lst.mean(dim="time").compute()
        return data

    def write(self, output_path):
        self.data.rio.to_raster(output_path)


