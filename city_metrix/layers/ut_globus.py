import ee
import geemap
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

from city_metrix.metrix_model import Layer, WGS_CRS, GeoExtent
from ..constants import GEOJSON_FILE_EXTENSION, GeoType
from ..metrix_dao import write_layer
from ..repo_manager import retrieve_cached_city_data2


class UtGlobus(Layer):
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

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None, 
                 force_data_refresh=False):
        # Note: spatial_resolution and resampling_method arguments are ignored.
        if self.city == "":
            raise Exception("'city' can not be empty. Check and select a city id from https://sat-io.earthengine.app/view/ut-globus")

        # Attempt to retrieve cached file based on layer_id.
        retrieved_cached_data, file_uri = retrieve_cached_city_data2(self, bbox, force_data_refresh)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        dataset = ee.FeatureCollection(f"projects/sat-io/open-datasets/UT-GLOBUS/{self.city}")
        ee_rectangle = bbox.to_ee_rectangle()
        ut_globus = dataset.filterBounds(ee_rectangle["ee_geometry"])
        try:
            building = geemap.ee_to_gdf(ut_globus).reset_index()
        except:
            building = gpd.GeoDataFrame(
                pd.DataFrame(columns=["index", "geometry", "Area", "Surface", "Volume", "height"]),
                geometry="geometry",
            )
            building.crs = WGS_CRS

        # filter out geom_type GeometryCollection
        gc_building = building[building.geom_type == "GeometryCollection"].copy()
        if len(gc_building) > 0:
            # select Polygons and Multipolygons from GeometryCollection
            gc_building["geometries"] = gc_building.apply(lambda x: [g for g in x.geometry.geoms], axis=1)
            gc_building_polygon = []
            # iterate over each row in gc_building
            for index, row in gc_building.iterrows():
                for geom in row["geometries"]:
                    # Check if the geometry is a Polygon or MultiPolygon
                    if isinstance(geom, Polygon) or isinstance(geom, MultiPolygon):
                        # Create a new row with the same attributes as the original row, but with the Polygon geometry
                        new_row = row.drop(["geometry", "geometries"])
                        new_row["geometry"] = geom
                        gc_building_polygon.append(new_row)
            if len(gc_building_polygon) > 0:
                # convert list to geodataframe
                gc_building_polygon = gpd.GeoDataFrame(gc_building_polygon, geometry="geometry")
                # replace GeometryCollection with Polygon, merge back to building
                building = building[building.geom_type != "GeometryCollection"]
                building = pd.concat([building, gc_building_polygon], ignore_index=True).reset_index()
            else:
                building = building[building.geom_type != "GeometryCollection"].reset_index()

        utm_crs = ee_rectangle["crs"]
        if building.crs.srs == WGS_CRS:
            building = building.to_crs(utm_crs)

        if bbox.geo_type == GeoType.CITY:
            write_layer(building, file_uri, self.GEOSPATIAL_FILE_FORMAT)

        return building
