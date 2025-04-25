import rasterio
import numpy as np
import rasterio.features

from city_metrix.metrix_model import Layer, GeoExtent
from . import NasaDEM
from ..constants import GTIFF_FILE_EXTENSION
from .overture_buildings_w_height import OvertureBuildingsHeight

DEFAULT_SPATIAL_RESOLUTION = 1


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
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        if self.city == "":
            raise Exception("'city' can not be empty. Check and select a city id from https://sat-io.earthengine.app/view/ut-globus")

        # Load the datasets
        buildings_gdf = OvertureBuildingsHeight(self.city).get_data(bbox)
        dem_da = NasaDEM().get_data(bbox, spatial_resolution=spatial_resolution)

        y_coords = dem_da.coords["y"].values
        needs_flip = y_coords[0] < y_coords[-1]
        if needs_flip:
            dem_da.values = np.flipud(dem_da.values)

        # Extract raster transform from DataArray attributes
        transform = rasterio.transform.from_bounds(
            dem_da.rio.bounds()[0], dem_da.rio.bounds()[1],
            dem_da.rio.bounds()[2], dem_da.rio.bounds()[3],
            dem_da.sizes["x"], dem_da.sizes["y"]
        )

        # Create a mask for all geometries at once
        all_masks = np.zeros((len(buildings_gdf), dem_da.sizes["y"], dem_da.sizes["x"]), dtype=bool)
        for i, geometry in enumerate(buildings_gdf.geometry):
            all_masks[i] = rasterio.features.geometry_mask(
                [geometry],
                transform=transform,
                out_shape=(dem_da.sizes["y"], dem_da.sizes["x"]),
                invert=True  # Mask inside the polygons
            )

        # Compute mean elevation for each masked area
        max_elevations = []
        for i in range(len(buildings_gdf)):
            masked_data = dem_da.where(all_masks[i])
            max_elevations.append(float(masked_data.max(skipna=True)))

        # Update GeoDataFrame with mean elevation and new heights
        buildings_gdf["max_elevation"] = max_elevations
        buildings_gdf["updated_height"] = buildings_gdf["height"] + buildings_gdf["max_elevation"]

        # Generate the updated raster layer
        building_dem_dsm = dem_da.copy(deep=True)
        for i in range(len(buildings_gdf)):
            building_dem_dsm.values[all_masks[i]] = (
                    buildings_gdf["max_elevation"].iloc[i] + buildings_gdf["height"].iloc[i]
            )

        if needs_flip:
            building_dem_dsm.values = np.flipud(building_dem_dsm.values)

        return building_dem_dsm
