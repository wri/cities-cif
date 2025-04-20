import os
from enum import Enum
from pathlib import Path

WGS_CRS = 'EPSG:4326'
WGS_EPSG_CODE = 4326

GTIFF_FILE_EXTENSION = 'tif'
GEOJSON_FILE_EXTENSION = 'geojson'
NETCDF_FILE_EXTENSION = 'nc'
CSV_FILE_EXTENSION = 'csv'

aws_s3_profile = 'cities-data-user'
default_publishing_env = 'dev'

# TODO replace with production value
RO_dashboard_layer_s3_bucket_uri = 's3://wri-cities-data-api'
RW_dashboard_layer_s3_bucket_uri = 's3://cities-test-sandbox' # 's3://wri-cities-data-api'
RW_dashboard_metric_s3_bucket_uri = 's3://cities-test-sandbox' # 's3://wri-cities-indicators'
RW_testing_s3_bucket_uri = 's3://cities-test-sandbox'

home_directory = os.path.join(Path.home(), 'CIF_layer_repository')
local_repo_uri = f'file://{home_directory}'

CITIES_DATA_API_URL = "cities-data-api.wri.org"

class GeoType(Enum):
    CITY = 0
    GEOMETRY = 1

class ProjectionType(Enum):
    GEOGRAPHIC = 0
    UTM = 1


class ModelClassName(Enum):
    LAYER = 0
    METRIC = 1