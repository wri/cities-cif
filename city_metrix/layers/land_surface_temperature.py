import odc.stac
import pystac_client

from .layer import Layer


class LandSurfaceTemperature(Layer):
    def __init__(self, start_date="2013-01-01", end_date="2023-01-01", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def get_data(self, bbox):
        catalog = pystac_client.Client.open("https://earth-search.aws.element84.com/v1")
        query = catalog.search(
            collections=["landsat-c2-l2"],
            datetime=[self.start_date, self.end_date],
            bbox=bbox,
        )

        lc2 = odc.stac.load(
            query.items(),
            bands=("lwir11", "qa_pixel"),
            resolution=30,
            bbox=bbox,
            chunks={'x': 1024, 'y': 1024, 'time': 1},
            groupby="solar_day",
            fail_on_error=False,
        )

        qa_lst = lc2.lwir11.where((lc2.qa_pixel & 24) == 0).where(lc2.lwir11 != 0)
        celsius_lst = (((qa_lst * 0.00341802) + 149) - 273.15)
        data = celsius_lst.mean(dim="time").compute()
        return data

    def write(self, output_path):
        self.data.rio.to_raster(output_path)


