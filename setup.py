from setuptools import find_packages, setup

setup(
    name="city_metrix",
    version="0.1.2",
    description="Module to calculate various metrics on cities.",
    packages=find_packages(),
    author="Justin Terry",
    license="MIT",
    install_requires=[
        "earthengine-api",
        "geocube",
        "odc-stac",
        "geemap",
        "pystac-client",
        "xarray-spatial",
        "xee",
        "rioxarray",
        "utm",
        "osmnx>=2.0.0",
        "geopandas",
        "xarray",
        "s3fs",
        "dask>=2023.11.0",
        "boto3",
        "overturemaps",
        "cdsapi",
        "timezonefinder",
        "scikit-image>=0.24.0",
        "exactextract>=0.2.0",
        "cfgrib"
    ],
)
