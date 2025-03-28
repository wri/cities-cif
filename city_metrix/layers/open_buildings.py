import ee
import geemap
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

from .layer import Layer, WGS_CRS
from .layer_geometry import GeoExtent, retrieve_cached_city_data, build_s3_names


class OpenBuildings(Layer):
    OUTPUT_FILE_FORMAT = 'geojson'

    """
    Attributes:
        countr: 3-letter code for country
    """
    def __init__(self, country='USA', **kwargs):
        super().__init__(**kwargs)
        self.country = country

    def get_layer_names(self):
        qualifier = "" if self.country else f"__{self.country}"
        layer_name, layer_id, file_format = build_s3_names(self, qualifier, None)
        return layer_name, layer_id, file_format

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None, allow_s3_cache_retrieval=False):
        #Note: spatial_resolution and resampling_method arguments are ignored.

        layer_name, layer_id, file_format = self.get_layer_names()
        retrieved_cached_data = retrieve_cached_city_data(bbox, layer_name, layer_id, file_format, allow_s3_cache_retrieval)
        if retrieved_cached_data is not None:
            return retrieved_cached_data

        dataset = ee.FeatureCollection(f"projects/sat-io/open-datasets/VIDA_COMBINED/{self.country}")
        ee_rectangle = bbox.to_ee_rectangle()
        open_buildings = (dataset
                          .filterBounds(ee_rectangle['ee_geometry'])
                          )
        openbuilds = geemap.ee_to_gdf(open_buildings).reset_index()

        # filter out geom_type GeometryCollection
        gc_openbuilds = openbuilds[openbuilds.geom_type == 'GeometryCollection']
        if len(gc_openbuilds) > 0:
            # select Polygons and Multipolygons from GeometryCollection
            gc_openbuilds['geometries'] = gc_openbuilds.apply(lambda x: [g for g in x.geometry.geoms], axis=1)
            gc_openbuilds_polygon = []
            # iterate over each row in gc_openbuilds
            for index, row in gc_openbuilds.iterrows():
                for geom in row['geometries']:
                    # Check if the geometry is a Polygon or MultiPolygon
                    if isinstance(geom, Polygon) or isinstance(geom, MultiPolygon):
                        # Create a new row with the same attributes as the original row, but with the Polygon geometry
                        new_row = row.drop(['geometry', 'geometries'])
                        new_row['geometry'] = geom
                        gc_openbuilds_polygon.append(new_row)
            if len(gc_openbuilds_polygon) > 0:
                # convert list to geodataframe
                gc_openbuilds_polygon = gpd.GeoDataFrame(gc_openbuilds_polygon, geometry='geometry')
                # replace GeometryCollection with Polygon, merge back to openbuilds
                openbuilds = openbuilds[openbuilds.geom_type != 'GeometryCollection']
                openbuilds = pd.concat([openbuilds, gc_openbuilds_polygon], ignore_index=True).reset_index()
            else:
                openbuilds = openbuilds[openbuilds.geom_type != 'GeometryCollection'].reset_index()

        utm_crs = ee_rectangle['crs']
        if openbuilds.crs.srs == WGS_CRS:
            openbuilds = openbuilds.to_crs(utm_crs)

        return openbuilds
