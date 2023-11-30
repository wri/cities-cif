from pystac_client import Client
import rioxarray
import xarray as xr
import ee

from .layer import Layer, get_utm_zone_epsg
from .. import EsaWorldCover, EsaWorldCoverClass
from .. import OSMClass,OpenStreetMap


class SmartCitiesLULC(Layer):
    def __init__(self, land_cover_class=None, **kwargs):
        super().__init__(**kwargs)
        self.land_cover_class = land_cover_class

    def get_data(self, bbox):
        esa1m = EsaWorldCover.get_data(bbox).rio.reproject(grid=())
        osm_gdf = OpenStreetMap().get_data(bbox)
        crs = get_utm_zone_epsg(bbox)

        make_geocube(
           vector_data=osm_gdf,
           measurements=["index"],
           like=esa1m,
        )

        ulu = xr.open_dataset(
            ee.ImageCollection("projects/wri-datalab/cities/urban_land_use/V1"),
            engine='ee',
            scale=5,
            crs=crs,
            geometry=ee.Geometry.Rectangle(*bbox)
        )
       
        ulu_data = ulu.ulu.compute()

        # ulu_data = ulu_data.where(ulu_data != self.NO_DATA_VALUE)

        # get in rioxarray format
        ulu_data = ulu_data.squeeze("time").transpose("Y", "X").rename({'X': 'x', 'Y': 'y'})





