from setuptools import find_packages, setup

setup(
    name="city_metrix",
    version="0.3.0",
    description="Module to calculate various metrics on cities.",
    packages=find_packages(),
    author="Justin Terry, Kenn Cartier",
    license="MIT",
    install_requires=[
        "earthengine-api",
        "geocube",
        "odc-stac",
        "geemap>=0.35.2",
        "pystac-client",
        "xarray",
        "xarray-spatial",
        "xee",
        "rioxarray",
        "utm",
        "osmnx>=2.0.1",
        "geopandas",
        "xarray",
        "s3fs",
        "dask[complete]<=2025.2.0",
        "boto3",
        "cdsapi",
        "timezonefinder",
        "scikit-image>=0.25.2",
        "exactextract>=0.2.0",
        "cfgrib",
        "scipy",
        "numpy",
        "overturemaps",
        "ipython",
        "pyopenssl>=23.0.0"
    ],
    package_data={
        'city_metrix': ['ut_globus_city_handler/global_ut_globus_cities.gpkg']
    },
)