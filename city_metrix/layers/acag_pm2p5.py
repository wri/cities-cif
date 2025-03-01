from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_image_collection
from .layer_geometry import GeoExtent


class AcagPM2p5(Layer):
    """
    Attributes:
        Only available year is 2022
    """

    def __init__(self, year=2022, return_above=0, **kwargs):
        super().__init__(**kwargs)
        self.year = year
        self.return_above = return_above

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None):
        acag_data = ee.Image(f'projects/wri-datalab/cities/aq/acag_annual_pm2p5_{self.year}')

        data = get_image_collection(
            ee.ImageCollection(acag_data),
            bbox.to_ee_rectangle(),
            1113.1949,
            "mean pm2.5 concentration"
        ).b1

        return data.where(data >= self.return_above)
