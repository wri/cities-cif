from time import sleep

import boto3
from rasterio.profiles import DefaultGTiffProfile
from rasterio.transform import from_bounds
from google.cloud import storage

from ..city import City
from ..io import read_vrt, read_tiles, initialize_ee, get_geo_name
import ee
import geemap
import rasterio.errors
import json
import time

import geopandas as gpd
import shapely.geometry
from pystac_client import Client

from odc.stac import configure_rio, stac_load
from shapely.geometry import box
import coiled
from distributed import Client


class Albedo:
    DATA_LAKE_PATH = "gs://gee-exports/albedo"

    def read(self, gdf: gpd.GeoDataFrame, snap_to=None):
        # if data not in data lake for city, extract
        geo_name = get_geo_name(gdf)
        uri = f"{self.DATA_LAKE_PATH}/{geo_name}-S2-albedo.tif"

        try:
            albedo = read_tiles(gdf, [uri], snap_to)
            return albedo
        except rasterio.errors.RasterioIOError as e:
            self.extract_gee(gdf)
            albedo = read_tiles(gdf, [uri], snap_to)
            return albedo

    def extract_gee(self, gdf: gpd.GeoDataFrame):
        initialize_ee()

        date_start = '2021-01-01'
        date_end = '2022-01-01'

        # define "low albedo" threshold
        LowAlbedoMax = 0.20  # EnergyStar steep slope minimum initial value is 0.25. 3-year value is 0.15. https://www.energystar.gov/products/building_products/roof_products/key_product_criteria

        # %%

        ## Configure methods

        # Read relevant Sentinel-2 data
        S2 = ee.ImageCollection("COPERNICUS/S2_SR")
        S2C = ee.ImageCollection("COPERNICUS/S2_CLOUD_PROBABILITY")

        MAX_CLOUD_PROB = 30
        S2_ALBEDO_EQN = '((B*Bw)+(G*Gw)+(R*Rw)+(NIR*NIRw)+(SWIR1*SWIR1w)+(SWIR2*SWIR2w))'

        ## METHODS

        ## get cloudmasked image collection

        def mask_and_count_clouds(s2wc, geom):
            s2wc = ee.Image(s2wc)
            geom = ee.Geometry(geom.geometry())
            is_cloud = ee.Image(s2wc.get('cloud_mask')).gt(MAX_CLOUD_PROB).rename('is_cloud')
            nb_cloudy_pixels = is_cloud.reduceRegion(
                reducer=ee.Reducer.sum().unweighted(),
                geometry=geom,
                scale=10,
                maxPixels=1e9
            )
            return s2wc.updateMask(is_cloud.eq(0)).set('nb_cloudy_pixels',
                                                       nb_cloudy_pixels.getNumber('is_cloud')).divide(10000)

        def mask_clouds_and_rescale(im):
            clouds = ee.Image(im.get('cloud_mask')).select('probability')
            return im.updateMask(clouds.lt(MAX_CLOUD_PROB)).divide(10000)

        def get_masked_s2_collection(roi, start, end):
            criteria = (ee.Filter.And(
                ee.Filter.date(start, end),
                ee.Filter.bounds(roi)
            ))
            s2 = S2.filter(criteria)  # .select('B2','B3','B4','B8','B11','B12')
            s2c = S2C.filter(criteria)
            s2_with_clouds = (ee.Join.saveFirst('cloud_mask').apply(**{
                'primary': ee.ImageCollection(s2),
                'secondary': ee.ImageCollection(s2c),
                'condition': ee.Filter.equals(**{'leftField': 'system:index', 'rightField': 'system:index'})
            }))

            def _mcc(im):
                return mask_and_count_clouds(im, roi)
                # s2_with_clouds=ee.ImageCollection(s2_with_clouds).map(_mcc)

            # s2_with_clouds=s2_with_clouds.limit(image_limit,'nb_cloudy_pixels')
            s2_with_clouds = ee.ImageCollection(s2_with_clouds).map(
                mask_clouds_and_rescale)  # .limit(image_limit,'CLOUDY_PIXEL_PERCENTAGE')
            return ee.ImageCollection(s2_with_clouds)

        # calculate albedo for images

        # weights derived from
        # S. Bonafoni and A. Sekertekin, "Albedo Retrieval From Sentinel-2 by New Narrow-to-Broadband Conversion Coefficients," in IEEE Geoscience and Remote Sensing Letters, vol. 17, no. 9, pp. 1618-1622, Sept. 2020, doi: 10.1109/LGRS.2020.2967085.
        def calc_s2_albedo(image):
            config = {
                'Bw': 0.2266,
                'Gw': 0.1236,
                'Rw': 0.1573,
                'NIRw': 0.3417,
                'SWIR1w': 0.1170,
                'SWIR2w': 0.0338,
                'B': image.select('B2'),
                'G': image.select('B3'),
                'R': image.select('B4'),
                'NIR': image.select('B8'),
                'SWIR1': image.select('B11'),
                'SWIR2': image.select('B12')
            }
            return image.expression(S2_ALBEDO_EQN, config).double().rename('albedo')

        boundary_geo = json.loads(gdf.to_json())
        boundary_geo_ee = geemap.geojson_to_ee(boundary_geo)

        ## S2 MOSAIC AND ALBEDO
        dataset = get_masked_s2_collection(boundary_geo_ee, date_start, date_end)
        s2_albedo = dataset.map(calc_s2_albedo)
        albedoMean = s2_albedo.reduce(ee.Reducer.mean())
        albedoMean = albedoMean.reproject(crs=ee.Projection('epsg:4326'), scale=10)

        # TODO hits pixel limit easily, need to just export to GCS and copy to S3
        file_name = get_geo_name(gdf) + '-S2-albedo'
        task = ee.batch.Export.image.toCloudStorage(**{
            'image': albedoMean,
            'description': file_name,
            'scale': 10,
            'region': boundary_geo_ee.geometry(),
            'fileFormat': 'GeoTIFF',
            'bucket': 'gee-exports',
            'formatOptions': {'cloudOptimized': True},
            'fileNamePrefix': 'albedo/' + file_name,
            'maxPixels': 1e13,
        })
        task.start()

        while task.active():
            print('Polling for task (id: {}).'.format(task.id))
            time.sleep(5)

        if task.status()["state"] == "COMPLETED":
            return f"{self.DATA_LAKE_PATH}/{file_name}"
        else:
            raise Exception(f"GEE task failed with status {task.status()['state']}, error message:\n{task.status()['error_message']}")

    def extract_dask(self, city: City):
        # TODO doesn't seem to be an easy way to access S2 cloud masks outside of GEE
        # create a remote Dask cluster with Coiled
        cluster = coiled.Cluster(name=city.id, worker_memory="32GiB", n_workers=100,
                                 use_best_zone=True,
                                 compute_purchase_option="spot_with_fallback")

        client = Client(cluster)

        catalog = Client.open("https://earth-search.aws.element84.com/v1")
        query = catalog.search(
            collections=["sentinel-2-l2a"], datetime=["2021-01-01", "2022-01-01"], bbox=city.bounds,
            limit=100
        )

        items = list(query.get_items())
        s2 = stac_load(
            items,
            bands=("red", "green", "blue", "nir", "swir16", "swir22"),
            crs="epsg:4326",
            resolution=0.0001,
            chunks={'latitude': 1024 * 4, 'longitude': 1024 * 4, 'time': 366},
        )

        Bw, Gw, Rw, NIRw, SWIR1w, SWIR2w = 0.2266, 0.1236, 0.1573, 0.3417, 0.1170, 0.0338
        albedo = ((s2.blue * Bw) + (s2.green * Gw) + (s2.red * Rw) + (s2.nir * NIRw) + (s2.swir16 * SWIR1w) + (s2.swir22 * SWIR2w))
        albedoMean = albedo.mean(dim="time").compute()

        _write_to_s3(albedoMean, city)


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
    s3_client.upload_file(file_name, "cities-indicators", f"data/albedo/test/{file_name}")
