from .metrics import *
import os
import ee
import warnings

# initialize ee
if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ and "GOOGLE_APPLICATION_USER" in os.environ:
    print("Authenticating to GEE with configured credentials file.")
    CREDENTIAL_FILE = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    GEE_SERVICE_ACCOUNT = os.environ["GOOGLE_APPLICATION_USER"]
    auth = ee.ServiceAccountCredentials(GEE_SERVICE_ACCOUNT, CREDENTIAL_FILE)
    ee.Initialize(auth, opt_url='https://earthengine-highvolume.googleapis.com')
else:
    print("Could not find GEE credentials file, so prompting authentication.")
    ee.Authenticate()
    ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')


# set for AWS requests
os.environ["AWS_REQUEST_PAYER"] = "requester"
warnings.filterwarnings('ignore', module='xee')