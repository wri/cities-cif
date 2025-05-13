import geopandas as gpd
import rasterio
import numpy as np
from rasterio.transform import Affine
from shapely.geometry import shape
from rasterio.features import shapes

from city_metrix.metrix_model import Layer, GeoExtent
from . import AverageNetBuildingHeight

from ..constants import GEOJSON_FILE_EXTENSION
from .overture_buildings import OvertureBuildings
from .ut_globus import UtGlobus

STANDARD_BUILDING_FLOOR_HEIGHT_M = 3.5
STANDARD_SINGLE_STORY_BUILDING_SQM = 50

class OvertureBuildingsHeight(Layer):
    GEOSPATIAL_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["city"]
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        city: city id from https://sat-io.earthengine.app/view/ut-globus
    """

    def __init__(self, city="", **kwargs):
        super().__init__(**kwargs)
        self.city = city

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None):
        # Note: spatial_resolution and resampling_method arguments are ignored.

        # Load the datasets
        overture_buildings = OvertureBuildings().get_data_with_caching(bbox)
        ut_globus = UtGlobus(self.city).get_data_with_caching(bbox)
        ut_globus = ut_globus.to_crs(overture_buildings.crs)

        # Step 1 and 2 Get heights from UTGlobus and Overture
        result_heights = join_overture_and_utglobus(overture_buildings, ut_globus)

        empty_height_blgs = result_heights[result_heights['height'].isna() | (result_heights['height'] == 0)]
        if empty_height_blgs.size > 0:
            # Determine height from num_floors column in Overture
            storied_bldgs = empty_height_blgs[empty_height_blgs['num_floors'].notna()]
            storied_bldgs['height'] = storied_bldgs['num_floors'] * STANDARD_BUILDING_FLOOR_HEIGHT_M
            storied_bldgs['height_source'] = 'Overture_floors'
            result_heights.loc[storied_bldgs.index, ['height', 'height_source']] = (
                storied_bldgs)[['height', 'height_source']]

            unstoried_bldgs = empty_height_blgs[empty_height_blgs['num_floors'].isna()]
            small_unstoried_bldgs = unstoried_bldgs[unstoried_bldgs.geometry.area <= STANDARD_SINGLE_STORY_BUILDING_SQM]
            small_unstoried_bldgs['height'] = STANDARD_BUILDING_FLOOR_HEIGHT_M
            small_unstoried_bldgs['height_source'] = 'Overture_small_area'
            result_heights.loc[small_unstoried_bldgs.index, ['height', 'height_source']] = (
                small_unstoried_bldgs)[['height', 'height_source']]

        empty_height_blgs = result_heights[result_heights['height'].isna() | (result_heights['height'] == 0)]
        if empty_height_blgs.size > 0:
            large_unstoried_height = get_anbh_for_buildings(bbox, empty_height_blgs)
            result_heights.loc[large_unstoried_height.index, ['height', 'height_source']] = (
                large_unstoried_height)[['height', 'height_source']]

        # set any remainders to one floor

        utm_crs = bbox.as_utm_bbox().crs
        result_heights = result_heights.to_crs(utm_crs)
        result_heights['height'] = result_heights['height'].round(2)

        return result_heights


def get_anbh_for_buildings(bbox, empty_height_blgs):
    from rasterio.features import geometry_mask

    anbh_cell_size = AverageNetBuildingHeight.DEFAULT_SPATIAL_RESOLUTION
    buffered_utm_bbox = bbox.buffer_utm_bbox(anbh_cell_size * 2)
    anbh_da = AverageNetBuildingHeight().get_data_with_caching(buffered_utm_bbox)

    # Ensure the CRS matches
    empty_height_blgs = empty_height_blgs.to_crs(anbh_da.rio.crs)

    # Iterate through polygons
    for index, row in empty_height_blgs.iterrows():
        polygon = row.geometry

        # Mask raster using polygon
        try:
            building_mask = geometry_mask([polygon], transform=anbh_da.rio.transform(), all_touched=True,
                                          invert=True, out_shape=anbh_da.shape)
            height_values = anbh_da.values[building_mask]
            # Only include features that arg large enough to overlap or touch a raster cell
            if height_values.size > 0:
                min_value = height_values.min().round(2)
                empty_height_blgs.loc[index, ['height', 'height_source']] = [min_value, 'ANBH']
        except Exception as e_msg:
            b=2

    populated_rows = empty_height_blgs[empty_height_blgs['height_source'] == 'ANBH']
    return populated_rows



def join_overture_and_utglobus(overture_buildings, ut_globus):
    # Perform spatial join - transferring height values directly during the join
    # Give preference to UTGlobus heights
    joined_data = gpd.sjoin(overture_buildings, ut_globus[["geometry", "height"]], how="left")

    # Add column to store the source of height information
    joined_data['height_source'] = np.nan

    if 'height' in overture_buildings.columns.to_list():
        # Ensure columns are managed correctly after join
        # If height_right (UTGlobus) is not null, use it; otherwise, use height_left (Overture)
        joined_data["height"] = joined_data["height_right"].fillna(joined_data["height_left"])
        joined_data.rename(
            columns={
                "height_left": "overture_height",
                "height_right": "utglobus_height",
            },
            inplace=True,
        )
    else:
        joined_data['utglobus_height'] = joined_data['height']
        joined_data["overture_height"] = None

        # Remove any index columns potentially misinterpreted
    joined_data.drop(columns=["index_right"], inplace=True)

    # Explicitly handle the unique uri_scheme for each row
    joined_data["id"] = joined_data.apply(lambda row: row["id"] if "id" in row else row.name, axis=1)

    # Fill missing height values
    joined_data["height"] = joined_data["height"].fillna(0)

    joined_data.drop_duplicates(subset='id')

    # Attribute with the data source
    joined_data.loc[(joined_data['utglobus_height'] == joined_data['height'])
                    & (~joined_data['utglobus_height'].isna())
                    & (~joined_data['height'].isna()), 'height_source'] = 'UTGlobus_height'
    joined_data.loc[(joined_data['overture_height'] == joined_data['height'])
                    & (~joined_data['overture_height'].isna())
                    & (~joined_data['height'].isna())
                    & (joined_data['height_source'].isna()), 'height_source'] = 'Overture_height'

    return joined_data
