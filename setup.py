from setuptools import setup

setup(
    name="cities-indicators_old",
    version="0.2",
    description="Module to calculate various metrics on cities.",
    packages=["city_metrix", "city_metrix.layers"],
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
    ],
)
