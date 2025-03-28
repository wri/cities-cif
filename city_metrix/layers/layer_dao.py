import os
import boto3
import requests

from city_metrix.constants import testing_aws_bucket, CITIES_DATA_API_URL


def get_city(city_id: str):
    query = f"https://{CITIES_DATA_API_URL}/cities/{city_id}"
    city = requests.get(query)
    if city.status_code in range(200, 206):
        return city.json()
    raise Exception("City not found")


def get_city_boundary(city_id: str, admin_level: str):
    query = f"https://{CITIES_DATA_API_URL}/cities/{city_id}/"
    city_boundary = requests.get(query)
    if city_boundary.status_code in range(200, 206):
        tuple_str = city_boundary.json()['bounding_box']
        bounds = _string_to_float_tuple(tuple_str)
        return bounds
    raise Exception("City boundary not found")


def _string_to_float_tuple(string_tuple):
    string_tuple = string_tuple.replace("[", "").replace("]", "")
    string_values = string_tuple.split(",")
    float_tuple = tuple(float(value.strip()) for value in string_values)
    return float_tuple

def get_s3_client():
    profile_name = os.getenv("S3_AWS_PROFILE")
    session = boto3.Session(profile_name=profile_name)
    s3_client = session.client('s3')
    return s3_client

def build_layer_name(class_name, qualifier_name):
    subclass_part = qualifier_name if qualifier_name is not None else ""
    layer_name = f"{class_name}{subclass_part}"
    return layer_name.lower()

def get_layer_names(class_name, qualifier_name, minor_qualifier, year_a, year_b, file_format):
    layer_name = build_layer_name(class_name, qualifier_name)
    minor_qualifier_part = f"{minor_qualifier}" if minor_qualifier is not None else ""
    year_a_part = f"__{year_a}" if year_a is not None else ""
    year_b_part = f"__{year_b}" if year_b is not None else ""
    layer_id = f"{layer_name}{minor_qualifier_part}{year_a_part}{year_b_part}.{file_format}"
    return layer_name, layer_id

def get_s3_file_key(layer_name, city_id, admin_level, layer_id, file_format):
    if os.environ['AWS_BUCKET'] == testing_aws_bucket:
        env = 'dev'
    else:
        env = 'prd'
    return f"data/{env}/{layer_name}/{file_format}/{city_id}__{admin_level}__{layer_id}"

def get_s3_file_url(file_key):
    aws_bucket = os.getenv("AWS_BUCKET")
    return f"s3://{aws_bucket}/{file_key}"


def get_file_key_from_s3_url(s3_url):
    file_key = '/'.join(s3_url.split('/')[3:])
    return file_key


def get_s3_variables(layer_obj, geo_extent):
    layer_name, layer_id, file_format = layer_obj.get_layer_names()
    city_id = geo_extent.city_id
    admin_level = geo_extent.admin_level
    file_key = get_s3_file_key(layer_name, city_id, admin_level, layer_id, file_format)
    file_url = get_s3_file_url(file_key)

    return file_key, file_url

def check_if_s3_file_exists(s3_client, file_key):
    aws_bucket = os.getenv("AWS_BUCKET")
    response = s3_client.list_objects_v2(Bucket=aws_bucket, Prefix=file_key)
    for obj in response.get('Contents', []):
        if obj['Key'] == file_key:
            return True
    return False


def write_geodataframe(path, data):
    if path.startswith("s3://"):
        write_geodataframe_to_s3(data, path)
    else:
        # write raster data to files
        output_path = os.path.dirname(path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        data.to_file(path, driver="GeoJSON")


def write_geodataframe_to_s3(data, path):
    import tempfile
    aws_bucket = os.getenv("AWS_BUCKET")
    file_key = get_file_key_from_s3_url(path)
    with tempfile.NamedTemporaryFile(suffix='.json', delete=True) as temp_file:
        temp_file_path = temp_file.name
        data.to_file(temp_file_path, driver="GeoJSON")

        s3_client = get_s3_client()
        s3_client.upload_file(
            temp_file_path, aws_bucket, file_key, ExtraArgs={"ACL": "public-read"}
        )


def write_dataarray(path, data):
    if path.startswith("s3://"):
        write_dataarray_to_s3(data, path)
    else:
        # write raster data to files
        output_path = os.path.dirname(path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        data.rio.to_raster(raster_path=path, driver="GTiff")


def write_dataarray_to_s3(data, path):
    import tempfile
    aws_bucket = os.getenv("AWS_BUCKET")
    file_key = get_file_key_from_s3_url(path)
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(f'{temp_dir}/temp.file', 'w') as temp_file:
            temp_file_path = temp_file.name
            data.rio.to_raster(raster_path=temp_file_path, driver="GTiff")
            s3_client = get_s3_client()
            try:
                s3_client.upload_file(
                    temp_file_path, aws_bucket, file_key, ExtraArgs={"ACL": "public-read"}
                )
            except Exception as e_msg:
                raise Exception(f"Failed to write data to S3 {file_key}")


def write_tile_grid(tile_grid, output_path, target_file_name):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    tile_grid_file_path = str(os.path.join(output_path, target_file_name))
    tg = tile_grid.drop(columns='fishnet_geometry', axis=1)
    tg.to_file(tile_grid_file_path)
