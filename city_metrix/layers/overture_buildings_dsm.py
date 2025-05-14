import math
import numpy as np
import rasterio
import xarray as xr
from exactextract import exact_extract
from rasterio.features import rasterize
from geocube.api.core import make_geocube
from rasterio.features import geometry_mask

from city_metrix.metrix_model import Layer, GeoExtent, validate_raster_resampling_method
from .nasa_dem import NasaDEM
from .overture_buildings_w_height import OvertureBuildingsHeight
from ..constants import GTIFF_FILE_EXTENSION


DEFAULT_SPATIAL_RESOLUTION = 1
DEFAULT_RESAMPLING_METHOD = "bilinear"


# This value was determined from a large warehouse as a worst-case example at lon/lat -122.76768,45.63313
BUILDING_INCLUSION_BUFFER_METERS = 500

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

        # Minimize the probability that buildings will bridge tile boundaries and therefor sample elevations for
        # only part of the full footprint by 1. buffering out the selection area, 2. filtering to contained buildings,
        # and 3. clipping back to the original selection area
        building_buffer = BUILDING_INCLUSION_BUFFER_METERS
        buffered_utm_bbox = bbox.buffer_utm_bbox(building_buffer)

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
            building_mask = geometry_mask([polygon], transform=DEM.rio.transform(), all_touched=True, invert=True, out_shape=DEM.shape)

            # get aggregated elevation within footprint
            # TODO Implement a more sophisticated method. See https://gfw.atlassian.net/browse/CDB-309
            DEM_values = DEM.values[building_mask]
            # Only include features that arg large enough to overlap or touch a raster cell
            if DEM_values.size > 0:
                footprint_elevation = DEM_values.max()

                # Add the building height and mean elevation
                DEM_updated.values[building_mask] = footprint_elevation + height

        # Clip back to the original AOI
        west, south, east, north = bbox.as_utm_bbox().bounds
        longitude_range = slice(west, east)
        latitude_range = slice(south, north)
        clipped_data = DEM_updated.sel(x=longitude_range, y=latitude_range)

        return clipped_data
