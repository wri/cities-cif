from .layer import Layer, get_utm_zone_epsg

from rioxarray.raster_array import RasterArray
import xarray as xr
import xee
import ee


class TreeCover(Layer):
    """
    Merged tropical and nontropical tree cover from WRI
    """
    
    NO_DATA_VALUE = 255

    def __init__(self, min_tree_cover=None, **kwargs):
        super().__init__(**kwargs)
        self.min_tree_cover = min_tree_cover

    def get_data(self, bbox):
        tropics = ee.ImageCollection('projects/wri-datalab/TropicalTreeCover')
        nontropics = ee.ImageCollection('projects/wri-datalab/TTC-nontropics')
        merged_ttc = tropics.merge(nontropics)
        ttc_image = merged_ttc.reduce(ee.Reducer.mean()).rename('ttc')
        crs = get_utm_zone_epsg(bbox)

        ds = xr.open_dataset(
            ee.ImageCollection(ttc_image),
            engine='ee',
            scale=10,
            crs=crs,
            geometry=ee.Geometry.Rectangle(*bbox)
        )

        data = ds.ttc.compute()
        data = data.where(data != self.NO_DATA_VALUE)

        # get in rioxarray format
        data = data.squeeze("time").transpose("Y", "X").rename({'X': 'x', 'Y': 'y'})

        if self.min_tree_cover is not None:
            data = data.where(data >= self.min_tree_cover)

        return data

