from .metrics import *
import os
import ee

# initialize ee
CREDENTIAL_FILE = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
GEE_SERVICE_ACCOUNT = os.environ["GOOGLE_APPLICATION_USER"]
auth = ee.ServiceAccountCredentials(GEE_SERVICE_ACCOUNT, CREDENTIAL_FILE)
ee.Initialize(auth, opt_url='https://earthengine-highvolume.googleapis.com')