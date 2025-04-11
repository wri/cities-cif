from pathlib import Path
from urllib.parse import urlparse

from city_metrix.constants import cif_production_aws_bucket_uri, testing_aws_bucket_uri

class CifCacheSettings:
    def __init__(self):
        self.cache_location_uri = None
        self.cache_environment = None
        self.aws_bucket = None

cif_cache_settings = CifCacheSettings()

"""
:param: uri - stores either an S3 bucket uri (e.g. 's3://<bucket_name>') or a file uri (e.g. 'file://<top_level_directgory>')
:param: env - specifies if cache path is for development ('dev') or production ('prd')
"""
def set_cache_settings(uri, env):
    parsed_uri = urlparse(uri)
    if parsed_uri.scheme not in ('s3','file'):
        raise Exception(f"Invalid uri parameter {uri}. The uri must start with either 's3://' or 'file://'")
    if env not in ('dev','prd'):
        raise Exception(f"Invalid env parameter {env}. Must be either 'dev' or 'prd'.")

    cif_cache_settings.cache_location_uri = uri
    cif_cache_settings.cache_environment = env
    cif_cache_settings.aws_bucket = cif_production_aws_bucket_uri if env == 'dev' else testing_aws_bucket_uri


def get_cache_settings():
    return cif_cache_settings.cache_location_uri, cif_cache_settings.cache_environment

def clear_cache_settings():
    cif_cache_settings.cache_location_uri = None
    cif_cache_settings.cache_environment = None
    cif_cache_settings.aws_bucket = None


def get_cached_file_key(layer_name, city_id, admin_level, layer_id):
    from pathlib import Path
    file_format = Path(layer_id).suffix.lstrip('.')
    env = cif_cache_settings.cache_environment
    file_key = f"data/{env}/{layer_name}/{file_format}/{city_id}__{admin_level}__{layer_id}"
    return file_key


def get_aws_bucket_name():
    bucket_uri = cif_cache_settings.aws_bucket
    aws_bucket = Path(bucket_uri).parts[1]
    return aws_bucket