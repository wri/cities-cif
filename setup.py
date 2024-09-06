from setuptools import setup, find_packages

setup(
    name="city_metrix",
    version="0.1.2",
    description="Module to calculate various metrics on cities.",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'city_metrix.models.building_classifier': [
            'building_classifier.pkl',
        ],
    },
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
        "osmnx",
        "geopandas",
        "s3fs",
        "dask>=2023.11.0",
        "boto3",
        "exactextract<=0.2.0.dev252",
        "overturemaps",
        "scikit-learn>=1.5.1",
    ],
)
