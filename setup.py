from setuptools import setup

setup(
    name="city_metrix",
    version="0.1.0",
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
