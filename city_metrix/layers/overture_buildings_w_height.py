import pandas as pd
import geopandas as gpd
import numpy as np

from city_metrix.metrix_model import Layer, GeoExtent, get_class_default_spatial_resolution
from . import AverageNetBuildingHeight
from ..constants import GEOJSON_FILE_EXTENSION, DEFAULT_DEVELOPMENT_ENV
from .overture_buildings import OvertureBuildings
from .ut_globus import UtGlobus

STANDARD_BUILDING_FLOOR_HEIGHT_M = 3.5
STANDARD_SINGLE_STORY_BUILDING_SQM = 50

class OvertureBuildingsHeight(Layer):
    OUTPUT_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = ["city"]

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
        # Specify DEFAULT_DEVELOPMENT_ENV since below are not Dashboard layers
        overture_buildings = OvertureBuildings().get_data(bbox=bbox)
        ut_globus = UtGlobus(self.city).get_data(bbox=bbox)
        if len(ut_globus) == 0:
            result_building_heights = overture_buildings
            if hasattr(overture_buildings, 'height'):
                result_building_heights.rename(
                    columns={"height": "overture_height"},
                    inplace=True,
                )
                result_building_heights['height'] = result_building_heights['overture_height']
                result_building_heights['height_source'] = 'Overture'
            else:
                result_building_heights['height'] = None

        else:
            ut_globus = ut_globus.to_crs(overture_buildings.crs)

            # Use the logic described in this page to determine height settings.
            # https://gfw.atlassian.net/wiki/spaces/CIT/pages/1971912734/Primary+Raster+Layers+for+Thermal+Comfort+Modeling

            # Step 1 and 2 Get heights from UTGlobus and Overture
            result_building_heights = _join_overture_and_utglobus(overture_buildings, ut_globus)

        # Step 3 and 4 Get heights based on two simple assumptions
        empty_height_blgs = result_building_heights[result_building_heights['height'].isna() |
                                                    (result_building_heights['height'] == 0)]
        if len(empty_height_blgs) > 0:
            # Determine height from num_floors column in Overture
            if 'num_floors' in empty_height_blgs.columns:
                storied_bldgs = empty_height_blgs[empty_height_blgs['num_floors'].notna()].copy()
                storied_bldgs['height'] = storied_bldgs['num_floors'] * STANDARD_BUILDING_FLOOR_HEIGHT_M
                storied_bldgs['height_source'] = 'Overture_floors'
                result_building_heights.loc[storied_bldgs.index, ['height', 'height_source']] = (
                    storied_bldgs)[['height', 'height_source']]

            # Set height base on assumption about size of small, one-storied buildings
            if 'num_floors' in empty_height_blgs.columns:
                unstoried_bldgs = empty_height_blgs[empty_height_blgs['num_floors'].isna()].copy()
            else:
                unstoried_bldgs = empty_height_blgs
            unstoried_bldgs = unstoried_bldgs[unstoried_bldgs.geometry.area <= STANDARD_SINGLE_STORY_BUILDING_SQM]
            unstoried_bldgs['height'] = STANDARD_BUILDING_FLOOR_HEIGHT_M
            unstoried_bldgs['height_source'] = 'Overture_small_area'
            result_building_heights.loc[unstoried_bldgs.index, ['height', 'height_source']] = (
                unstoried_bldgs)[['height', 'height_source']]

        # Step 6 Estimate height using the ANBH Built-H dataset
        empty_height_blgs = result_building_heights[result_building_heights['height'].isna() | (result_building_heights['height'] == 0)]
        if len(empty_height_blgs) > 0:
            large_unstoried_height = _get_anbh_for_buildings(bbox, empty_height_blgs)
            result_building_heights.loc[large_unstoried_height.index, ['height', 'height_source']] = (
                large_unstoried_height)[['height', 'height_source']]

        # Step 7 Set any remainders to one floor, however no building should remain at this point
        empty_height_blgs = result_building_heights[result_building_heights['height'].isna() | (result_building_heights['height'] == 0)]
        if len(empty_height_blgs) > 0:
            empty_height_blgs.loc[:, ['height', 'height_source']] = [STANDARD_BUILDING_FLOOR_HEIGHT_M, 'Remainder']
            result_building_heights.loc[empty_height_blgs.index, ['height', 'height_source']] = (
                empty_height_blgs)[['height', 'height_source']]

        utm_crs = bbox.as_utm_bbox().crs
        result_building_heights = result_building_heights.to_crs(utm_crs)

        result_building_heights["height"] = pd.to_numeric(result_building_heights["height"], errors="coerce")
        result_building_heights['height'] = result_building_heights['height'].round(2)

        return result_building_heights

def _list_to_string(val, delimiter=", "):
    if isinstance(val, list):
        # Convert all elements to string, skip None
        return delimiter.join(str(x) for x in val if x is not None)
    return "" if pd.isna(val) else str(val)

def _join_overture_and_utglobus(overture_buildings, ut_globus):
    # Perform spatial join - transferring height values directly during the join
    # Give preference to UTGlobus heights
    joined_data = gpd.sjoin(overture_buildings, ut_globus[["geometry", "height"]], how="left")

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

    # Get mode or median of heights from UT Globus for buildings that overlapped with UTGlobus buildings
    filtered_data = joined_data.dropna(subset=['utglobus_height'])
    mode_or_median_df  = filtered_data.groupby('id')['utglobus_height'].apply(mode_or_median).reset_index()
    merged_gdf = filtered_data.merge(mode_or_median_df.rename(columns={'utglobus_height': 'mode_or_med_utglobus_height'}), on='id')
    thinned_gdf = merged_gdf.drop(columns=['utglobus_height', 'height'])

    # flatten multi-valued columns
    thinned_gdf['sources'] = thinned_gdf['sources'].apply(_list_to_string)
    thinned_gdf['names'] = thinned_gdf['names'].apply(_list_to_string)

    overture_with_globus_height = thinned_gdf.drop_duplicates()
    overture_with_globus_height['height'] = overture_with_globus_height['mode_or_med_utglobus_height']
    # Assign source as UTGlobus
    overture_with_globus_height['height_source'] = 'UTGlobus'

    # Get buildings that did not overlap with a UTGlobus value
    overture_without_globus_height = joined_data[~joined_data['id'].isin(mode_or_median_df['id'])]
    overture_without_globus_height = overture_without_globus_height.drop(columns=['utglobus_height'])
    overture_without_globus_height['mode_or_med_utglobus_height'] = np.nan
    overture_without_globus_height['height_source'] = np.where(overture_without_globus_height['overture_height'].notna(), 'Overture', '')

    # Combine Globus and non-Globus records
    df_combined = gpd.GeoDataFrame(pd.concat([overture_with_globus_height, overture_without_globus_height], ignore_index=True)).reset_index(drop=True)

    return df_combined



def mode_or_median(series):
    mode_values = series.mode()
    if mode_values.size == 1:
        return mode_values.iloc[0]
    else:
        y =  custom_median(series)
        return y


def custom_median(series):
    sorted_values = np.sort(series)
    n = len(sorted_values)

    if n % 2 == 1:  # Odd length, return the center value
        return sorted_values[n // 2]
    else:  # Even length, return the lower of the two middle values
        return sorted_values[n // 2 - 1]


def _get_anbh_for_buildings(bbox, empty_height_blgs):
    from rasterio.features import geometry_mask

    # Expand the AOI to ensure coverage of all buildings by ANBH
    anbh_obj = AverageNetBuildingHeight()
    anbh_cell_size = get_class_default_spatial_resolution(anbh_obj)
    buffered_utm_bbox = bbox.buffer_utm_bbox(anbh_cell_size * 2)
    anbh_da = anbh_obj.get_data(bbox=buffered_utm_bbox)

    # Ensure the CRS matches
    empty_height_blgs = empty_height_blgs.to_crs(anbh_da.rio.crs).copy()

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
            print(e_msg)

    populated_rows = empty_height_blgs[empty_height_blgs['height_source'] == 'ANBH']
    return populated_rows