import os
import warnings

import ee

# initialize ee
if (
    "GOOGLE_APPLICATION_CREDENTIALS" in os.environ
    and "GOOGLE_APPLICATION_USER" in os.environ
):
    print("Authenticating to GEE with configured credentials file.")
    CREDENTIAL_FILE = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    GEE_SERVICE_ACCOUNT = os.environ["GOOGLE_APPLICATION_USER"]
    if CREDENTIAL_FILE.endswith(".json"):
        auth = ee.ServiceAccountCredentials(
            GEE_SERVICE_ACCOUNT, key_file=CREDENTIAL_FILE
        )
    else:
        auth = ee.ServiceAccountCredentials(
            GEE_SERVICE_ACCOUNT, key_data=CREDENTIAL_FILE
        )
    ee.Initialize(auth, opt_url="https://earthengine-highvolume.googleapis.com")
else:
    print("Could not find GEE credentials file, so prompting authentication.")
    ee.Authenticate()
    ee.Initialize(opt_url="https://earthengine-highvolume.googleapis.com")


# set for AWS requests
os.environ["AWS_REQUEST_PAYER"] = "requester"

# Get access base_id using https://airtable.com/developers/web/api/introduction
# get airtable parameters
AIRTABLE_PERSONAL_API_KEY = None
AIRTABLE_METRICS_BASE_ID = None
if (
    "AIRTABLE_PERSONAL_API_KEY" in os.environ
    and "AIRTABLE_METRICS_BASE_ID" in os.environ
):
    AIRTABLE_PERSONAL_API_KEY = os.environ["AIRTABLE_PERSONAL_API_KEY"]
    AIRTABLE_METRICS_BASE_ID = os.environ["AIRTABLE_METRICS_BASE_ID"]
else:
    print("env not found")
    # raise Exception("Environment variables for Airtable not found.")

# disable warning messages
warnings.filterwarnings("ignore", module="xee")
warnings.filterwarnings("ignore", module="dask")
warnings.filterwarnings("ignore", module="xarray")

from .metrics import *
