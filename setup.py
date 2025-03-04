from setuptools import find_packages, setup

setup(
    name="city_metrix",
    version="0.1.2",
    python_requires='3.10',
    description="Module to calculate various metrics on cities.",
    packages=find_packages(),
    author="Justin Terry",
    license="MIT",
    install_requires=[
        "earthengine-api>=0.1.411",
        "geocube>=0.4.2",
        "gdal>=3.10.0",
        "odc-stac>=0.3.8",
        "geemap>=0.32.0",
        "pystac-client>=0.7.5",
        "xarray>=2024.7.0",
        "xarray-spatial>=0.3.7",
        "xee>=0.0.15",
        "rioxarray>=0.15.0",
        "utm>=0.7.0",
        "osmnx>=2.0.0",
        "geopandas>=1.0.1",
        "xarray>=2024.7.0",
        "s3fs>=2024.5.0",
        "dask>=2023.11.0",
        "boto3>=1.34.124",
        "overturemaps>=0.6.0",
        "cdsapi>=0.7.5",
        "timezonefinder>=6.5.2",
        "scikit-image>=0.24.0",
        "exactextract>=0.2.0",
        "cfgrib>=0.9.15.0",
        "scipy>=1.13.1",
        "numpy>=1.23.0"
    ],
)
