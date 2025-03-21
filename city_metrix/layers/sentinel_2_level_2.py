import odc.stac
import pystac_client
from city_metrix.layers.layer_geometry import GeoExtent, retrieve_cached_data

from .layer import Layer


class Sentinel2Level2(Layer):
    LAYER_ID = "sentinel_2_level_2"
    OUTPUT_FILE_FORMAT = 'tif'

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
                 allow_s3_cache_retrieval=False):
        if spatial_resolution is not None:
            raise Exception('spatial_resolution can not be specified.')
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')

        retrieved_cached_data = retrieve_cached_data(bbox, self.LAYER_ID, None, self.OUTPUT_FILE_FORMAT
                                                     ,allow_s3_cache_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        geographic_bounds = bbox.as_geographic_bbox().bounds
        catalog = pystac_client.Client.open("https://earth-search.aws.element84.com/v1")
        query = catalog.search(
            collections=["sentinel-2-l2a"],
            datetime=[self.start_date, self.end_date],
            bbox=geographic_bounds
        )

        cfg = {
            "sentinel-2-l2a": {
                "assets": {
                    "*": {"data_type": "uint16", "nodata": 0},
                    "SCL": {"data_type": "uint8", "nodata": 0},
                    "visual": {"data_type": "uint8", "nodata": 0},
                },
            },
            "*": {"warnings": "ignore"},
        }

        s2 = odc.stac.load(
            list(query.items()),
            bands=(*self.bands, "scl"),
            resolution=10,
            stac_cfg=cfg,
            bbox=geographic_bounds,
            chunks={'x': 1024 * 4, 'y': 1024 * 4, 'time': 1},
        )

        # Scene Classfication Layer (SCL) categorizes pixels at a scene level
        # 0 = no data
        # 3 = cloud shadows
        # 8 = medium probability of clouds
        # 9 = high probability of clouds
        # 10 = thin cirrus clouds

        # mask out no data, clouds and cloud shadows
        cloud_masked = s2.where(s2 != 0).where(s2.scl != 3).where(s2.scl != 8).where(s2.scl != 9).where(
            s2.scl != 10)

        return cloud_masked.drop_vars("scl")
