from setuptools import find_packages, setup

setup(
    name="city_metrix",
    version="0.3.0",
    description="Module to calculate various metrics on cities.",
    packages=find_packages(),
    author="Justin Terry, Kenn Cartier",
    license="MIT",
    install_requires=[
        "boto3>=1.38.18",
        "cdsapi>=0.7.6",
        "cfgrib>=0.9.15.0",
        "dask[complete]>=2025.5.0",
        "earthengine-api>=1.5.15",
        "exactextract>=0.2.2",
        "gdal>=3.10.3",
        "geemap>=0.35.3",
        "geocube>=0.7.1",
        "geopandas>=1.0.1",
        "ipython>=9.2.0",
        "matplotlib>=3.10.3",
        "numpy>=2.2.6",
        "odc-stac>=0.4.0",
        "osmnx>=2.0.3",
        "overturemaps>=0.14.0",
        "pystac-client>=0.8.6",
        "rioxarray>=0.19.0",
        "s3fs>=0.4.2",
        "scikit-image>=0.25.2",
        "scipy>=1.15.2",
        "timeout-decorator>=0.5.0",
        "timezonefinder>=6.5.9",
        "utm>=0.7.0",
        "xarray>=2025.4.0",
        "xarray-spatial>=0.4.0",
        "xee>=0.0.20"
    ],
    package_data={
        'city_metrix': ['ut_globus_city_handler/global_ut_globus_cities.gpkg']
    },
)

