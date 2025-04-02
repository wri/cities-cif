# Cities Indicator Framework

The Cities Indicator Framework (CIF) is a set of Python tools to make it easier to calculate zonal statistics for cities by providing a standardized set of data layers for inputs and a common framework for using those layers to calculate indicators.

## Quick start

* If all you want to do is use the CIF, the quickest way to get started is to use our [WRI Cities Indicator Framework Colab Notebook](https://colab.research.google.com/drive/1PV1H-godxJ6h42p74Ij9sdFh3T0RN-7j#scrollTo=eM14UgpmpZL-)

## Installation
* `pip install git+https://github.com/wri/cities-cif@v0.1.2` to install a specific version.
* `pip install git+https://github.com/wri/cities-cif/releases/latest` gives you the latest stable release.
* `pip install git+https://github.com/wri/cities-cif` gives you the main branch with is not stable.

NOTE: If you have already installed the package and want to update to the latest code you may need to add the `--force-reinstall` flag

## PR Review

0. Prerequisites
1. Git
   * On Windows I recommend WSL [https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-git](https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-git)
2. [https://cli.github.com/](https://cli.github.com/)
   * On MacOS I recommend the Homebrew option
   * If you don't have an ssh key, it will install one for you
3. Conda (or Mamba) to install dependencies
   * If you have Homebrew `brew install --cask miniconda`

## Dependencies

There are 2 ways to install dependencies. Choose one...

### Conda

`conda env create -f environment.yml` or `conda env update -f environment.yml`

### Setuptools

`python setup.py`
NOTE: If you are using this method you may want to use something like pyenv to manage Python environments

## Credentials

To run the module,

  1. You need access to Google Earth Engine
  2. Install <https://cloud.google.com/sdk/docs/install>
  3. If you want to use the ERA5 and CAMS layers:
     1. you need to install the [Climate Data Store (CDS) Application Program Interface (API)](https://cds.climate.copernicus.eu/how-to-api)
     2. create a .cdsapirc file in your home directory and save the key you acquired from https://cds.climate.copernicus.eu/how-to-api
        1. Note: you do not need to specify any url's in the .cdsapirc file since they are specified in code.
  4. You must create an AWS credentials file in your system as described here: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html
     1. The credentials file must have a profile named "cities-data-user" with credentials for the cities-data-user IAM user
     
### Interactive development

For most people working in a notebook or IDE the script should walk you through an interactive authentication process. You will just need to be logged in to your Google account that has access to GEE in your browser.

### Programmatic access

If you have issues with this or need to run the script as part of an automated workflow we have a GEE-enabled GCP service account that can be used. Get in touch with Saif or Chris to ask about getting the credetials.

Set the following environment variables:
* GOOGLE_APPLICATION_CREDENTIALS: The path of GCP credentials JSON file containing your private key.
* GOOGLE_APPLICATION_USER: The email for your GCP user.

For example, you could set the following in your `~/.zshrc` file:

```
export GOOGLE_APPLICATION_USER=developers@citiesindicators.iam.gserviceaccount.com
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials/file
```

### Execution via scripts
1. Individual layers and indicators can be downloaded for specified cities using the cities-cif-portal codebase at https://github.com/wri/cities-cif-portal 
2. The spatial extent of the requested layer AOI can be specified through the GeoExtent class in two ways for an AOI:
   1. the geometric bounds as a tuple of floats, such as:
   2. the city_id and aoi_id as a json snippet, such as:
      '''
      {"city_id": "BRA-Florianopolis", "aoi_id": "city_admin_level"}
      '''
      * Note: the city_id and aoi_id may be determined via the Cities Indicators API at https://dev.cities-data-api.wri.org/docs

## How to contribute

All are welcome to contribute by creating a [Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests). We try to follow the [Github Flow](https://docs.github.com/en/get-started/quickstart/github-flow) workflow.

See [PR Review](docs/pr_review.md) for more details and options on how to review a PR.

See the [developer docs](docs/developer.md) to learn more about how to add data layers and indicators.
