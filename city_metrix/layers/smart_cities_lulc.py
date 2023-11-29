from pystac_client import Client
import rioxarray
import xarray as xr

from .layer import Layer


class SmartCitiesLULC(Layer):
    def __init__(self, land_cover_class=None, **kwargs):
        super().__init__(**kwargs)
        self.land_cover_class = land_cover_class

    def get_data(self, bbox):
       esa1m = EsaWorldCover.get_data(bbox).rio.reproject(grid=())
       osm_gdf = OSMOpenSpace().get_data(bbox)

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







