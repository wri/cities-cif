import boto3
import pystac_client
from rasterio.profiles import DefaultGTiffProfile
from rasterio.transform import from_bounds

from .layer import Layer
import rasterio.errors

from odc.stac import stac_load

from .sentinel_2_level_2 import Sentinel2Level2


class Albedo(Layer):
    def __init__(self, start_date="2021-01-01", end_date="2022-01-01", threshold=None, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.threshold = threshold

    def get_data(self, bbox):
        s2 = Sentinel2Level2(
            bands=("R", "G", "B", "NIR", "SWIR1", "SWIR2"),
            start_date=self.start_date,
            end_date=self.end_date,
        ).get_data(bbox) / 10000

        Bw, Gw, Rw, NIRw, SWIR1w, SWIR2w = 0.2266, 0.1236, 0.1573, 0.3417, 0.1170, 0.0338
        albedo = (s2.B * Bw) + (s2.G * Gw) + (s2.R * Rw) + (s2.NIR * NIRw) + \
                 (s2.SWIR1 * SWIR1w) + (s2.SWIR2 * SWIR2w)
        albedoMean = albedo.mean(dim="time")
        data = albedoMean.compute()

        if self.threshold is not None:
            data = data.where(data > self.threshold)

        return data

