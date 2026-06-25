# Installation

## Install the package

```bash
# A specific released version
pip install git+https://github.com/wri/cities-cif@v0.1.2

# The latest stable release
pip install git+https://github.com/wri/cities-cif/releases/latest

# The main branch (not guaranteed stable)
pip install git+https://github.com/wri/cities-cif
```

If you already have the package installed and want to pick up the latest code, add `--force-reinstall`.

Alternatively, clone the repo and use the bundled environment file:

```bash
conda env create -f environment.yml   # or: conda env update -f environment.yml
```

## Credentials

`city_metrix` pulls data from Google Earth Engine and caches results to S3, so importing the package authenticates against both on startup.

### Google Earth Engine

You need access to Google Earth Engine and the [Cloud SDK](https://cloud.google.com/sdk/docs/install) installed locally.

- **Interactive use** (notebook/IDE): the first `import city_metrix` walks you through a browser-based auth flow against your Google account.
- **Programmatic / automated use**: set these environment variables to use a GEE-enabled service account instead:

  ```bash
  export GOOGLE_APPLICATION_USER=developers@citiesindicators.iam.gserviceaccount.com
  export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials/file
  ```

### AWS S3

Layer and metric results are cached to S3, and the package needs AWS credentials at import time to set up its S3 client.

- Create an AWS credentials file as described in the [AWS CLI docs](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html), with a profile named `cities-data-dev`.
- Or set `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` directly in the environment.
- Or set `AWS_PROFILE` to point at a different named profile.

### ERA5 / CAMS layers only

If you plan to use the ERA5 or CAMS climate layers, you additionally need a [Climate Data Store (CDS) API](https://cds.climate.copernicus.eu/how-to-api) key, stored in a `.cdsapirc` file in your home directory.

!!! warning "Import has side effects"
    `import city_metrix` immediately authenticates to GEE and initializes an S3 client — there is no lazy/deferred setup. Make sure credentials are in place *before* importing the package, even if you only plan to call a single layer.

## Verify it works

```python
from city_metrix.layers import TreeCover
TreeCover()
```

If this runs without raising an authentication error, you're set up correctly. Continue to the [Quickstart](quickstart.md).
