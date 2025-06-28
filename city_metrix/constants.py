import os
from enum import Enum
from pathlib import Path

WGS_CRS = 'EPSG:4326'
WGS_EPSG_CODE = 4326

GTIFF_FILE_EXTENSION = 'tif'
GEOJSON_FILE_EXTENSION = 'geojson'
NETCDF_FILE_EXTENSION = 'nc'
CSV_FILE_EXTENSION = 'csv'

DEFAULT_PRODUCTION_ENV = 'prd' # 'prd'
DEFAULT_DEVELOPMENT_ENV = 'dev'
DEFAULT_STAGING_ENV = 'staging'

RO_DASHBOARD_LAYER_S3_BUCKET_URI = 's3://wri-cities-data-api'
RW_CACHE_S3_BUCKET_URI = 's3://cities-test-sandbox' # 's3://cities-cache-store'
RW_TESTING_S3_BUCKET_URI = 's3://cities-test-sandbox'

repo_directory = os.path.join(Path.home(), 'CIF_layer_repository')
LOCAL_REPO_URI = f'file://{repo_directory}'

CITIES_DATA_API_URL = "cities-data-api.wri.org"  # "dev.cities-data-api.wri.org"

class GeoType(Enum):
    CITY = 0
    GEOMETRY = 1

class ProjectionType(Enum):
    GEOGRAPHIC = 0
    UTM = 1

class ModelClassName(Enum):
    LAYER = 0
    METRIC = 1
