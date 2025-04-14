import os

from city_metrix.file_cache_config import get_cif_s3_bucket_name
from city_metrix.metrix_dao import get_s3_client
from tests.resources.conftest import get_target_folder_path, USE_WGS_BBOX


def delete_file_on_s3(s3_client, file_key):
    aws_bucket = get_cif_s3_bucket_name()
    s3_client.delete_object(Bucket=aws_bucket, Key=file_key)

def delete_file_on_os(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def cleanup_cache_files(file_key, file_path):
    s3_client = get_s3_client()
    delete_file_on_s3(s3_client, file_key)
    delete_file_on_os(file_path)

def prep_output_path(output_folder, file_name):
    file_path = os.path.join(output_folder, file_name)
    if os.path.isfile(file_path):
        os.remove(file_path)
    return file_path

def verify_file_is_populated(file_path):
    is_populated = True if os.path.getsize(file_path) > 0 else False
    return is_populated

def get_file_count_in_folder(dir_path):
    count = 0
    for path in os.scandir(dir_path):
        if path.is_file():
            count += 1
    return count

def cleanup_cache_files(cache_scheme, key_file, file_path):
    if cache_scheme == 's3':
        s3_client = get_s3_client()
        delete_file_on_s3(s3_client, key_file)
    else:
        target_folder = get_target_folder_path()
        cache_file_path = os.path.join(target_folder, key_file)
        delete_file_on_os(cache_file_path)
    if file_path is not None:
        delete_file_on_os(file_path)

def get_test_bbox(sample_box):
    bbox = sample_box if USE_WGS_BBOX else sample_box.as_geographic_bbox()
    return bbox
