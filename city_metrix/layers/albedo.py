import boto3
import pystac_client
from rasterio.profiles import DefaultGTiffProfile
from rasterio.transform import from_bounds

from .layer import Layer
import rasterio.errors

from odc.stac import stac_load


class Albedo(Layer):
    def __init__(self, start_date="2021-01-01", end_date="2022-01-01", threshold=None, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.threshold = threshold

    def get_data(self, bbox):
        catalog = pystac_client.Client.open("https://earth-search.aws.element84.com/v1")
        query = catalog.search(
            collections=["sentinel-2-l2a"],
            datetime=[self.start_date, self.end_date],
            bbox=bbox
        )

        cfg = {
            "sentinel-2-l2a": {
                "assets": {
                    "*": {"data_type": "uint16", "nodata": 0},
                    "SCL": {"data_type": "uint8", "nodata": 0},
                    "visual": {"data_type": "uint8", "nodata": 0},
                },
                "aliases": {"R": "red", "G": "green", "B": "blue", "NIR": "nir", "SWIR1": "swir16", "SWIR2": "swir22",
                            "SCL": "scl"},
            },
            "*": {"warnings": "ignore"},
        }

        s2 = stac_load(
            list(query.items()),
            bands=("R", "G", "B", "NIR", "SWIR1", "SWIR2", "SCL"),
            resolution=10,
            stac_cfg=cfg,
            bbox=bbox,
            chunks={'x': 1024 * 4, 'y': 1024 * 4, 'time': 1},
        )

        # Scene Classfication Layer (SCL) categorizes pixels at a scene level
        # 0 = no data
        # 3 = cloud shadows
        # 8 = medium probability of clouds
        # 9 = high probability of clouds
        # 10 = thin cirrus clouds

        # mask out no data, clouds and cloud shadows
        cloud_masked = s2.where(s2 != 0).where(s2["SCL"] != 3).where(s2["SCL"] != 8).where(s2["SCL"] != 9).where(
            s2 != 10) / 10000

        Bw, Gw, Rw, NIRw, SWIR1w, SWIR2w = 0.2266, 0.1236, 0.1573, 0.3417, 0.1170, 0.0338
        albedo = ((cloud_masked.B * Bw) + (cloud_masked.G * Gw) + (cloud_masked.R * Rw) + (cloud_masked.NIR * NIRw) + (
                    cloud_masked.SWIR1 * SWIR1w) + (cloud_masked.SWIR2 * SWIR2w))
        albedoMean = albedo.mean(dim="time")
        data = albedoMean.compute()

        if self.threshold is not None:
            data = data.where(data > self.threshold)

        return data


def _write_to_s3(result, city: City):
    file_name = f"{city.id}-S2-albedo.tif"
    width, height = result.data.shape[1], result.data.shape[0]
    transform = from_bounds(*city.bounds, width, height)
    profile = DefaultGTiffProfile(transform=transform, width=width, height=height, crs=4326, blockxsize=400,
                                  blockysize=400, count=1, dtype=result.dtype)

    # write tile to file
    with rasterio.open(file_name, "w", **profile) as dst:
        dst.write(result.data, 1)

    s3_client = boto3.client("s3")
    s3_client.upload_file(file_name, "cities-indicators_old", f"data/albedo/test/{file_name}")
