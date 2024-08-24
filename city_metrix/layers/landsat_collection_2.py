import odc.stac
import pystac_client
from jupyterlab.utils import deprecated

from .layer import Layer

@deprecated
class LandsatCollection2(Layer):
    def __init__(self, bands, start_date="2013-01-01", end_date="2023-01-01", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.bands = bands

    def get_data(self, bbox):
        catalog = pystac_client.Client.open("https://earth-search.aws.element84.com/v1")
        query = catalog.search(
            collections=["landsat-c2-l2"],
            datetime=[self.start_date, self.end_date],
            bbox=bbox,
        )

        lc2 = odc.stac.load(
            query.items(),
            bands=(*self.bands, "qa_pixel"),
            resolution=30,
            bbox=bbox,
            chunks={'x': 1024, 'y': 1024, 'time': 1},
            groupby="solar_day",
            fail_on_error=False,
        )

        # TODO: Determine how to output xarray

        qa_lst = lc2.where((lc2.qa_pixel & 24) == 0)
        return qa_lst.drop_vars("qa_pixel")
