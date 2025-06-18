import os
import shutil

from city_metrix import s3_client
from city_metrix.constants import RW_CACHE_S3_BUCKET_URI
from city_metrix.metrix_dao import remove_scheme_from_uri
from tests.resources.conftest import get_target_folder_path, USE_WGS_BBOX
from tests.tools.general_tools import create_target_folder

def prep_output_path(output_folder, model_name, file_name):
    folder_path = os.path.join(output_folder, model_name)
    create_target_folder(folder_path, False)

    file_path = os.path.join(folder_path, file_name)
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

def cleanup_cache_files(base_class_name, cache_scheme, key_file, file_path):
    if key_file is not None:
        if cache_scheme == 's3':
            delete_cache_file_on_s3(key_file)
        else:
            target_folder = get_target_folder_path()
            cache_file_path = os.path.join(target_folder, key_file)
            delete_path_on_os(cache_file_path)
    if file_path is not None:
        delete_path_on_os(file_path)

def delete_cache_file_on_s3(file_key):
    s3_bucket = remove_scheme_from_uri(RW_CACHE_S3_BUCKET_URI)
    s3_client.delete_object(Bucket=s3_bucket, Key=file_key)

def delete_path_on_os(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

def get_test_bbox(sample_box):
    bbox = sample_box if USE_WGS_BBOX else sample_box.as_geographic_bbox()
    return bbox
