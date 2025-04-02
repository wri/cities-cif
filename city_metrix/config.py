from urllib.parse import urlparse

CIF_CACHE_LOCATION_URI = None
CIF_CACHE_ENVIRONMENT = None

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

    global CIF_CACHE_LOCATION_URI
    global CIF_CACHE_ENVIRONMENT
    CIF_CACHE_LOCATION_URI = uri
    CIF_CACHE_ENVIRONMENT = env

def get_cache_settings():
    return CIF_CACHE_LOCATION_URI, CIF_CACHE_ENVIRONMENT
