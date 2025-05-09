import math
import numpy as np
from rasterio.features import geometry_mask
from city_metrix.metrix_model import Layer, GeoExtent, validate_raster_resampling_method
from . import NasaDEM
from ..constants import GTIFF_FILE_EXTENSION
from .overture_buildings_w_height import OvertureBuildingsHeight

DEFAULT_SPATIAL_RESOLUTION = 1
DEFAULT_RESAMPLING_METHOD = 'bilinear'

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
                 resampling_method:str=DEFAULT_RESAMPLING_METHOD):
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)

        # Minimize the probability that buildings will bridge tile boundaries and therefor sample elevations for
        # only part of the full footprint by 1. buffering out the selection area, 2. filtering to contained buildings,
        # and 3. clipping back to the original selection area
        building_buffer = 500
        buffered_utm_bbox = bbox.buffer_utm_bbox(building_buffer)

        # Load buildings and sub-select to ones fully contained in buffered area
        raw_buildings_gdf = OvertureBuildingsHeight(self.city).get_data(buffered_utm_bbox)
        contained_buildings_gdf = (
            raw_buildings_gdf)[raw_buildings_gdf.geometry.apply(lambda x: x.within(buffered_utm_bbox.polygon))]

        DEM = NasaDEM().get_data(buffered_utm_bbox, spatial_resolution=spatial_resolution, resampling_method=resampling_method)

        # Create an array to store the updated DEM values
        DEM_updated = DEM.copy()

        for _, building in contained_buildings_gdf.iterrows():
            height = building['height']
            polygon = building['geometry']

            # Rasterize footprint to create a mask
            building_mask = geometry_mask([polygon], transform=DEM.rio.transform(), invert=True, out_shape=DEM.shape)

            # mean elevation within footprint
            footprint_elevation = DEM.values[building_mask].mean()

            # Add the building height and mean elevation
            DEM_updated.values[building_mask] = footprint_elevation + height

        # Clip back to the original AOI
        west, south, east, north = bbox.as_utm_bbox().bounds
        longitude_range = slice(west, east)
        latitude_range = slice(south, north)
        clipped_data = DEM_updated.sel(x=longitude_range, y=latitude_range)

        return clipped_data
