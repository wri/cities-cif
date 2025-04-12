from enum import Enum

WGS_CRS = 'EPSG:4326'
WGS_EPSG_CODE = 4326

GTIFF_FILE_EXTENSION = 'tif'
GEOJSON_FILE_EXTENSION = 'geojson'
NETCDF_FILE_EXTENSION = 'nc'
CSV_FILE_EXTENSION = 'csv'

# TODO replace with production value
cif_production_s3_bucket_uri = 's3://cities-dev-sandbox' # 's3://wri-cities-data-api'
cif_dashboard_s3_bucket_uri = 's3://wri-cities-data-api'

cif_testing_s3_bucket_uri = 's3://cities-dev-sandbox'
ctcm_development_s3_bucket_uri = 's3://cities-tcm-dev-sandbox'


aws_s3_profile = 'cities-data-user'

#TODO In near-term, the cities-dat-api must be replaced by dev.cities-data-api after the dev.. API stabilizes.
# CITIES_DATA_API_URL = "dev.cities-data-api.wri.org"
CITIES_DATA_API_URL = "cities-data-api.wri.org"

class GeoType(Enum):
    CITY = 0
    GEOMETRY = 1

class ProjectionType(Enum):
    GEOGRAPHIC = 0
    UTM = 1
