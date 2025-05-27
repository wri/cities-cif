import numpy as np
from rasterio.features import geometry_mask
from city_metrix.metrix_model import Layer, GeoExtent, validate_raster_resampling_method
from . import FabDEM
from ..constants import GTIFF_FILE_EXTENSION
from .overture_buildings_w_height import OvertureBuildingsHeight

DEFAULT_SPATIAL_RESOLUTION = 1
DEFAULT_RESAMPLING_METHOD = 'bilinear'

# This value was determined from a large warehouse as a worst-case example at lon/lat -122.76768,45.63313
BUILDING_INCLUSION_BUFFER_METERS = 500

class OvertureBuildingsDSM(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
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

        # Minimize the probability that buildings will bridge tile boundaries and thereby sample elevations for
        # only part of the full footprint by: 1. buffering out AOI, 2. filtering buildings to contained buildings,
        # 3. masking buffered DEM by footprint and determining elevation of footprint, 4. masking unbuffered DEM
        # with footprint, 5. add footprint elevation to unbuffered DEM.
        # Population of the unbuffered DEM ensures that AOI is correct.
        building_buffer = BUILDING_INCLUSION_BUFFER_METERS
        buffered_utm_bbox = bbox.buffer_utm_bbox(building_buffer)

        # Load buildings and sub-select to ones fully contained in buffered area
        raw_buildings_gdf = OvertureBuildingsHeight(self.city).get_data(buffered_utm_bbox)
        contained_buildings_gdf = (
            raw_buildings_gdf)[raw_buildings_gdf.geometry.apply(lambda x: x.within(buffered_utm_bbox.polygon))]

        buffered_dem = FabDEM().get_data(buffered_utm_bbox, spatial_resolution=1, resampling_method='bilinear')
        query_dem = FabDEM().get_data(bbox, spatial_resolution=1, resampling_method='bilinear')
        # Change will be applied only to the copy to avoid doubly changing the raster
        result_dem = query_dem.copy()

        for _, building in contained_buildings_gdf.iterrows():
            height = building['height']
            polygon = building['geometry']

            # Rasterize footprint to create a mask.
            buffered_building_mask = geometry_mask([polygon], transform=buffered_dem.rio.transform(),
                                          all_touched=False, invert=True, out_shape=buffered_dem.shape)

            # get aggregated elevation within footprint
            # TODO Implement a more sophisticated method. See https://gfw.atlassian.net/browse/CDB-309
            buffered_dem_values = buffered_dem.values[buffered_building_mask]
            # Only include features that are large enough to overlap or touch a raster cell
            if buffered_dem_values.size > 0:
                footprint_elevation = buffered_dem_values.max()
                roof_elev = footprint_elevation + height

                # Rasterize footprint to create a mask. Use all_touched=False to produce narrower shape of footprint.
                building_mask = geometry_mask([polygon], transform=query_dem.rio.transform(), all_touched=False,
                                              invert=True, out_shape=query_dem.shape)

                # Only include features that are large enough to overlap or touch a raster cell
                if np.any(building_mask):
                    result_dem.values[building_mask] = roof_elev

        return result_dem
