from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_utm_zone_epsg


class UrbanLandUse(Layer):
    def __init__(self, band='lulc', **kwargs):
        super().__init__(**kwargs)
        self.band = band

    def get_data(self, bbox):
        crs = get_utm_zone_epsg(bbox)
        dataset = ee.ImageCollection("projects/wri-datalab/cities/urban_land_use/V1")
        
        if dataset.filterBounds(ee.Geometry.BBox(*bbox)).size().getInfo() == 0:
            ulu = ee.Image.constant(1).clip(ee.Geometry.BBox(*bbox)).rename('lulc')
        else:
            ulu = (dataset
                .filterBounds(ee.Geometry.BBox(*bbox))
                .select(self.band)
                .reduce(ee.Reducer.firstNonNull())
                .rename('lulc')
                )

        ds = xr.open_dataset(
            ee.ImageCollection(ulu),
            engine='ee',
            scale=5,
            crs=crs,
            geometry=ee.Geometry.Rectangle(*bbox),
            chunks={'X': 512, 'Y': 512}
        )

        with ProgressBar():
            print("Extracting ULU layer:")
            data = ds.lulc.compute()

        # get in rioxarray format
        data = data.squeeze("time").transpose("Y", "X").rename({'X': 'x', 'Y': 'y'})

        return data
