import os
import warnings

# set for AWS requests
os.environ["AWS_REQUEST_PAYER"] = "requester"

# disable warning messages
warnings.filterwarnings("ignore", module="xee")
warnings.filterwarnings("ignore", module="dask")
warnings.filterwarnings("ignore", module="xarray")
