from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_utm_zone_epsg


class BuiltUpHeight(Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox):
        crs = get_utm_zone_epsg(bbox)
        # Notes for Heat project:
        # https://ghsl.jrc.ec.europa.eu/ghs_buH2023.php
        # ANBH is the average height of the built surfaces, USE THIS
        # AGBH is the amount of built cubic meters per surface unit in the cell
        # ee.ImageCollection("projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_R2023A")
        
        built_height = ee.Image("JRC/GHSL/P2023A/GHS_BUILT_H/2018")
        
        ds = xr.open_dataset(
            ee.ImageCollection(built_height),
            engine='ee',
            scale=100,
            crs=crs,
            geometry=ee.Geometry.Rectangle(*bbox),
            chunks={'X': 512, 'Y': 512}
        )

        with ProgressBar():
            print("Extracting built up height layer:")
            data = ds.built_height.compute()
        
        # get in rioxarray format
        data = data.squeeze("time").transpose("Y", "X").rename({'X': 'x', 'Y': 'y'})

        return data
