import geopandas as gpd
import shapely

from .layer import Layer, get_utm_zone_epsg

class Isochrone(Layer):
    def __init__(self, geojson_filepath, **kwargs):
        super().__init__(**kwargs)
        gdf = gpd.read_file(geojson_filepath)
        self.gdf = gpd.GeoDataFrame({'is_accessible': [1] * len(gdf), 'geometry': gdf.to_crs('EPSG:4326')['geometry']}).to_crs('EPSG:4326').set_crs('EPSG:4326').set_geometry('geometry')
        
    def get_data(self, bbox):
        return self.gdf.clip(shapely.box(*bbox))
