from setuptools import setup

setup(
    name="city_metrix",
    version="0.1.1",
    description="Module to calculate various metrics on cities.",
    packages=["city_metrix", "city_metrix.layers", "city_metrix.metrics", "city_metrix.models", "city_metrix.models.building_classifier"],
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
        "cartoframes",
        "utm",
        "osmnx",
        "geopandas",
        "s3fs",
        "dask>=2023.11.0",
        "boto3",
        "exactextract",
        "overturemaps",
        "scikit-learn==1.5.0",
    ],
)
