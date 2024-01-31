from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_utm_zone_epsg


class AverageNetBuildingHeight(Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox):
        crs = get_utm_zone_epsg(bbox)
        # https://ghsl.jrc.ec.europa.eu/ghs_buH2023.php
        # ANBH is the average height of the built surfaces, USE THIS
        # AGBH is the amount of built cubic meters per surface unit in the cell
        # US - ee.ImageCollection("projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_R2023A")
        # GLOBE - ee.Image("projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_GLOBE_R2023A")
        
        anbh = ee.Image("projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_GLOBE_R2023A")
        
        ds = xr.open_dataset(
            ee.ImageCollection(anbh),
            engine='ee',
            scale=100,
            crs=crs,
            geometry=ee.Geometry.Rectangle(*bbox),
            chunks={'X': 512, 'Y': 512}
        )

        with ProgressBar():
            print("Extracting ANBH layer:")
            data = ds.b1.compute()
        
        # get in rioxarray format
        data = data.squeeze("time").transpose("Y", "X").rename({'X': 'x', 'Y': 'y'})

        return data
