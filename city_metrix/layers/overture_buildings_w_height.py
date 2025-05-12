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

        joined_heights = join_overture_and_utglobus(overture_buildings, ut_globus)

        invalid_height_blgs = joined_heights[joined_heights['height'].isna() | (joined_heights['height'] == 0)]
        if invalid_height_blgs.size > 0:
            meters_per_floor = 3
            storied_bldgs = invalid_height_blgs[invalid_height_blgs['num_floors'].notna()]
            storied_bldgs['height'] = storied_bldgs['num_floors'] * meters_per_floor

            sq_meters_residential_bldg = 200
            unstoried_bldgs = invalid_height_blgs[invalid_height_blgs['num_floors'].isna()]
            small_unstoried_bldgs = unstoried_bldgs[unstoried_bldgs.geometry.area <= sq_meters_residential_bldg]
            small_unstoried_bldgs['height'] = meters_per_floor

            large_unstoried_bldgs = unstoried_bldgs[unstoried_bldgs.geometry.area > sq_meters_residential_bldg]
            anbh_df = AverageNetBuildingHeight().get_data_with_caching(bbox)
            # anbh_gdf = rasterize_reproject_anbh(anbh_df, overture_buildings.crs.to_string())
            large_unstoried_height = get_anbh_for_buildings(anbh_df, large_unstoried_bldgs)



        utm_crs = bbox.as_utm_bbox().crs
        joined_heights = joined_heights.to_crs(utm_crs)

        return joined_heights


def get_anbh_for_buildings(raster_gdf, buildings_gdf):
    import geopandas as gpd
    import xarray as xr
    import rioxarray as rxr

    # Ensure the CRS matches
    buildings_gdf = buildings_gdf.to_crs(raster_gdf.rio.crs)

    # Initialize a list to store mean values
    mean_values = []

    # Iterate through polygons
    for _, row in buildings_gdf.iterrows():
        polygon = row.geometry

        # Mask raster using polygon
        try:
            clipped = raster_gdf.rio.clip([polygon], raster_gdf.rio.crs)

            # Compute mean excluding NaN values
            mean_value = float(clipped.mean().values) if not clipped.isnull().all() else None
            mean_values.append(mean_value)
        except:
            b=2

    # Add the mean values as a new column
    buildings_gdf["mean_raster_value"] = mean_values

    return buildings_gdf

def rasterize_reproject_anbh(anbh_df, target_crs):
    # Vectorize anbh and convert to geodataframe
    crs_transform = anbh_df.attrs.get("crs_transform")
    transform = Affine(*crs_transform)
    mask = anbh_df != 0  # Mask non-zero values
    results = shapes(anbh_df, mask=mask, transform=transform)

    # Convert to GeoDataFrame with preserved values
    geometries = []
    values = []

    for geom, value in results:
        geometries.append(shape(geom))
        values.append(value)

    # Create a GeoDataFrame
    anbh_gdf = gpd.GeoDataFrame({"Value": values, "geometry": geometries})

    # transform CRS
    source_crs = anbh_df.attrs.get('crs', None)
    anbh_with_crs_gdf = anbh_gdf.set_crs(source_crs)
    result_anbh_gdf = anbh_with_crs_gdf.to_crs(target_crs)

    return result_anbh_gdf

def join_overture_and_utglobus(overture_buildings, ut_globus):
    # Perform spatial join - transferring height values directly during the join
    joined_data = gpd.sjoin(overture_buildings, ut_globus[["geometry", "height"]], how="left")

    # Ensure columns are managed correctly after join
    # If height_right is not null, use it; otherwise, use height_left
    if 'height' in overture_buildings.columns.to_list():
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

    return joined_data
