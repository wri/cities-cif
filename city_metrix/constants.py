import os
from enum import Enum
from pathlib import Path

WGS_CRS = 'EPSG:4326'
WGS_EPSG_CODE = 4326

GTIFF_FILE_EXTENSION = 'tif'
GEOJSON_FILE_EXTENSION = 'geojson'
NETCDF_FILE_EXTENSION = 'nc'
CSV_FILE_EXTENSION = 'csv'
JSON_FILE_EXTENSION = 'json'

DEFAULT_PRODUCTION_ENV = 'published'  # 'prd'
DEFAULT_DEVELOPMENT_ENV = 'pre-release'  # 'dev'
DEFAULT_STAGING_ENV = 'staging'  # not used in new file storage structure

CIF_DASHBOARD_LAYER_S3_BUCKET_URI = 's3://wri-cities-data-api'
CIF_CACHE_S3_BUCKET_URI = 's3://wri-cities-indicators'  # 's3://cities-test-sandbox' # 's3://cities-cache-store'
CIF_TESTING_S3_BUCKET_URI = 's3://cities-test-sandbox'  # not used in new file storage structure

local_cache_directory = os.path.join(Path.home(), 'CIF_local_cache')
LOCAL_CACHE_URI = f'file://{local_cache_directory}'

FILE_KEY_ADMINBOUND_MARKER = False
FILE_KEY_URBEXTBOUND_MARKER = True
CUSTOM_CACHED_DIFFERENTLY = False

CITIES_DATA_API_URL = "https://dev.cities-data-api.wri.org" # at later date, consider switching to "cities-data-api.wri.org". Ask Saif

# CTCM features
CTCM_CACHE_S3_BUCKET_URI = 's3://wri-cities-tcm'
CTCM_MAX_TILE_BUFFER_M = 600
# Ensure complete TCM tile-sampling coverage by adding extra buffer
CTCM_PADDED_AOI_BUFFER = CTCM_MAX_TILE_BUFFER_M + 100

MULTI_TILE_TILE_INDEX_FILE = 'geotiff_index.json'
PROCESSING_KNOWN_ISSUE_FLAG = '**KNOWN_ISSUE**'

class GeoType(Enum):
    CITY = 0
    GEOMETRY = 1


class ProjectionType(Enum):
    GEOGRAPHIC = 0
    UTM = 1


class ModelClassName(Enum):
    LAYER = 0
    METRIC = 1
