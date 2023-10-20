from setuptools import setup

setup(
    name="cities-indicators",
    version="0.1",
    description="Module to calculate cities indicators",
    packages=["cities_indicators"],
    author="Justin Terry",
    license="MIT",
    install_requires=[
        "boto3",
        "coiled",
        "earthengine-api",
        "geemap",
        "geocube",
        "google-cloud-storage",
        "odc-stac",
        "pystac-client",
        "xarray-spatial"
    ],
)
