import os

from city_metrix.file_cache_config import get_cif_s3_bucket_name
from city_metrix.metrix_dao import get_s3_client
from tests.resources.conftest import RESOLUTION_MTHD, FIXED_RESOLUTION, RESOLUTION_MULTIPLIER, USE_WGS_BBOX
from tests.tools.general_tools import get_class_default_spatial_resolution

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

def get_test_resolution(cls):
    if RESOLUTION_MTHD == 'fixed':
        target_res = FIXED_RESOLUTION
    else:
        target_res = RESOLUTION_MULTIPLIER * get_class_default_spatial_resolution(cls)
    return target_res

def get_test_bbox(sample_box):
    bbox = sample_box if USE_WGS_BBOX else sample_box.as_geographic_bbox()
    return bbox
