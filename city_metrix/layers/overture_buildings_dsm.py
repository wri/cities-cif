import numpy as np
import rasterio
import xarray as xr
from exactextract import exact_extract
from rasterio.features import rasterize
from geocube.api.core import make_geocube

from city_metrix.metrix_model import Layer, GeoExtent, validate_raster_resampling_method
from . import NasaDEM
from ..constants import GTIFF_FILE_EXTENSION
from .overture_buildings_w_height import OvertureBuildingsHeight

DEFAULT_SPATIAL_RESOLUTION = 1
DEFAULT_RESAMPLING_METHOD = "bilinear"


class OvertureBuildingsDSM(Layer):
    GEOSPATIAL_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["city"]
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        city: city id from https://sat-io.earthengine.app/view/ut-globus
    """

    def __init__(self, city="", **kwargs):
        super().__init__(**kwargs)
        self.city = city

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method: str = DEFAULT_RESAMPLING_METHOD):
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)

        # Load the datasets
        buildings_gdf = OvertureBuildingsHeight(self.city).get_data(bbox)
        dem_da = NasaDEM().get_data(bbox, spatial_resolution=spatial_resolution, resampling_method=resampling_method)

        # Calculate mode elevation and estimate building elevations
        buildings_gdf["mode_elevation"] = exact_extract(dem_da, buildings_gdf, ["mode"], output="pandas")["mode"]
        buildings_gdf["elevation_estimate"] = buildings_gdf["height"] + buildings_gdf["mode_elevation"]

        # Rasterize the buildings_gdf into an xarray Dataset
        overture_buildings_raster = make_geocube(
            vector_data=buildings_gdf,
            measurements=["elevation_estimate"],
            like=dem_da,
        ).elevation_estimate
        overture_buildings_raster = overture_buildings_raster.rio.reproject_match(dem_da)

        # take values from overture_buildings_raster where ever overture_buildings_raster is not NaN,
        # and wherever overture_buildings_raster is NaN it will fill in from dem_da
        composite_bldg_dem = overture_buildings_raster.combine_first(dem_da)

        return composite_bldg_dem
