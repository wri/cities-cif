from pystac_client import Client
import rioxarray
import xarray as xr

from .layer import Layer


class SmartCitiesLULC(Layer):
    def __init__(self, land_cover_class=None, **kwargs):
        super().__init__(**kwargs)
        self.land_cover_class = land_cover_class

    def get_data(self, bbox):
       raise NotImplementedError("Need to implement once layers in GCS")






