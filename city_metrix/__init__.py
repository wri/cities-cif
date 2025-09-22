import os
import warnings
from pathlib import Path

import boto3
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
    print("Authenticating GEE by prompting authentication through Google API.")
    ee.Authenticate()
    ee.Initialize(opt_url="https://earthengine-highvolume.googleapis.com")

# initialize aws
credentials_file_path = Path(os.path.join(Path.home(),'.aws', 'credentials'))
config_file_path = Path(os.path.join(Path.home(),'.aws', 'config'))

if "AWS_PROFILE" in os.environ:
    aws_profile = os.environ["AWS_PROFILE"]
else:
    aws_profile = "cities-data-dev"

if (
    "AWS_ACCESS_KEY_ID" in os.environ
    and "AWS_SECRET_ACCESS_KEY" in os.environ
):
    s3_client = boto3.client('s3', region_name='us-east-1')
elif credentials_file_path.exists() or config_file_path.exists():
    try:
        session = boto3.Session(profile_name=aws_profile, region_name='us-east-1')
        s3_client = session.client('s3')
    except Exception as e:
        raise Exception(f"Could not initialize S3 client with profile '{aws_profile}': {e}")
else:
    try:
        session = boto3.Session()
        s3_client = session.client('s3')
    except Exception as e:
        raise Exception(f"Could not initialize S3 client without a profile: {e}")

# set for AWS requests
os.environ["AWS_REQUEST_PAYER"] = "requester"

# disable warning messages
warnings.filterwarnings("ignore", module="xee")
warnings.filterwarnings("ignore", module="dask")
warnings.filterwarnings("ignore", module="xarray")

from .metrics import *
