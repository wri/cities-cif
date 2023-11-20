from setuptools import setup

setup(
    name="cities-indicators_old",
    version="0.1",
    description="Module to calculate cities indicators_old",
    packages=["cities_indicators", "cities_indicators.indicators_old", "cities_indicators.layers"],
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
        "xarray-spatial",
        "cartoframes"
    ],
)
