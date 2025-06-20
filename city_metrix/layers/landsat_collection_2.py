import odc.stac
import pystac_client

from city_metrix.metrix_model import Layer, GeoExtent
from ..constants import GTIFF_FILE_EXTENSION


class LandsatCollection2(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["bands"]
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        bands:
        start_date: starting date for data retrieval
        end_date: ending date for data retrieval
    """
    def __init__(self, bands, start_date="2013-01-01", end_date="2023-01-01", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.bands = bands

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None,
                 force_data_refresh=False):
        if spatial_resolution is not None:
            raise Exception('spatial_resolution can not be specified.')
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')

        geographic_bounds = bbox.as_geographic_bbox().bounds
        catalog = pystac_client.Client.open("https://earth-search.aws.element84.com/v1")
        query = catalog.search(
            collections=["landsat-c2-l2"],
            datetime=[self.start_date, self.end_date],
            bbox=geographic_bounds,
        )

        lc2 = odc.stac.load(
            query.items(),
            bands=(*self.bands, "qa_pixel"),
            resolution=30,
            bbox=geographic_bounds,
            chunks={'x': 1024, 'y': 1024, 'time': 1},
            groupby="solar_day",
            fail_on_error=False,
        )

        qa_lst = lc2.where((lc2.qa_pixel & 24) == 0)
        data = qa_lst.drop_vars("qa_pixel")

        return data

