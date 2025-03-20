import os
import boto3
import requests

#TODO In near-term, the cities-dat-api must be replaced by dev.cities-data-api after the dev.. API stabilizes.
# CITIES_DATA_API_URL = "dev.cities-data-api.wri.org"
CITIES_DATA_API_URL = "cities-data-api.wri.org"

def get_city(city_id: str):
    query = f"https://{CITIES_DATA_API_URL}/cities/{city_id}"
    city = requests.get(query)
    if city.status_code in range(200, 206):
        return city.json()
    raise Exception("City not found")

def get_city_boundary(city_id: str, admin_level: str):
    query = f"https://{CITIES_DATA_API_URL}/cities/{city_id}/{admin_level}/geojson"
    city_boundary = requests.get(query)
    if city_boundary.status_code in range(200, 206):
        return city_boundary.json()
    raise Exception("City boundary not found")


def get_s3_client():
    session = boto3.Session(profile_name=os.getenv("S3_AWS_PROFILE"))
    s3_client = session.client('s3')
    return s3_client

def get_s3_layer_name(city_id, admin_level, layer_id, year, file_format):
    return f"{city_id}__{admin_level}__{layer_id}__{year}.{file_format}"

def get_s3_file_key(city_id, file_format, file_name):
    return f"cid/dev/{city_id}/{file_format}/{file_name}"

def get_s3_file_url(file_key):
    aws_profile = os.getenv("S3_AWS_PROFILE")
    return f"s3://{aws_profile}/{file_key}"


def get_file_key_from_s3_url(s3_url):
    file_key = '/'.join(s3_url.split('/')[3:])
    return file_key


def check_if_s3_file_exists(s3_client, file_key):
    aws_bucket = os.getenv("AWS_BUCKET")
    response = s3_client.list_objects_v2(Bucket=aws_bucket, Prefix=file_key)
    for obj in response.get('Contents', []):
        if obj['Key'] == file_key:
            return True
    return False


def write_file_to_s3(data, path):
    import tempfile
    aws_bucket = os.getenv("AWS_BUCKET")
    file_key = get_file_key_from_s3_url(path)
    with tempfile.NamedTemporaryFile(suffix='.tif', delete=True) as temp_file:
        temp_file_path = temp_file.name
        data.rio.to_raster(raster_path=temp_file_path, driver="COG")

        s3_client = get_s3_client()
        s3_client.upload_file(
            temp_file_path, aws_bucket, file_key, ExtraArgs={"ACL": "public-read"}
        )


def set_environment_variable(variable_name, variable_value):
    os.environ[variable_name] = variable_value
