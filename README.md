# cities-cif

## Dependencies
### Conda
`conda env create -f environment.yml`

## Credentials
To run the module, you need to a GEE-enabled GCP service account to read and write data.

Set the following environment variables:
- GOOGLE_APPLICATION_CREDENTIALS: The path of GCP credentials JSON file containing your private key.
- GOOGLE_APPLICATION_USER: The email for your GCP user.
- GCS_BUCKET: The GCS bucket to read and write data from. 

## How to contribute
The code has the following structure:

- The `layers` subpackage contains all data raster or vector data used for metrics inhering from the base `Layer` class
    - All layers must implement a `get_data` function that accept a bbox and returns a rioxarray-format xarray with the data in the bbox
    - rioxarray format means only `x` and `y` dimensions, in that order
    - New layers based off existing layers should re-use that layer's data
    - The Layer subclass will handle actually running zonal statistics
- Pre-canned "indicator" analyses are defined as functions in `metrics.py`
    - Indicator analyses should use calculate using layer classes and `Layer` zonal stats API
- To utilize dask for bigger jobs, dask cluster must be initialized outside this library