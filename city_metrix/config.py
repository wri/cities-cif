CIF_CACHE_LOCATION_URI = None
CIF_CACHE_ENVIRONMENT = None

def set_cache_settings(uri, env):
    global CIF_CACHE_LOCATION_URI
    global CIF_CACHE_ENVIRONMENT
    CIF_CACHE_LOCATION_URI = uri
    CIF_CACHE_ENVIRONMENT = env

def get_cache_settings():
    return CIF_CACHE_LOCATION_URI, CIF_CACHE_ENVIRONMENT
