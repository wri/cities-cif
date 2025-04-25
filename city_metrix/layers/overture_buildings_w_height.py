import geopandas as gpd

from city_metrix.metrix_model import Layer, GeoExtent

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
        if self.city == "":
            raise Exception("'city' can not be empty. Check and select a city id from https://sat-io.earthengine.app/view/ut-globus")

        # Load the datasets
        overture_buildings = OvertureBuildings().get_data_with_caching(bbox)
        ut_globus = UtGlobus(self.city).get_data_with_caching(bbox)

        # Ensure both GeoDataFrames are using the same coordinate reference system
        ut_globus = ut_globus.to_crs(overture_buildings.crs)

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
            joined_data['utglobus_height2'] = joined_data['height']
            joined_data["overture_height"] = None


        # Remove any index columns potentially misinterpreted
        joined_data.drop(columns=["index_right"], inplace=True)

        # Explicitly handle the unique uri_scheme for each row
        joined_data["id"] = joined_data.apply(lambda row: row["id"] if "id" in row else row.name, axis=1)

        # Fill missing height values
        joined_data["height"] = joined_data["height"].fillna(0)

        joined_data.drop_duplicates(subset='id')

        utm_crs = bbox.as_utm_bbox().crs
        joined_data = joined_data.to_crs(utm_crs)

        return joined_data
