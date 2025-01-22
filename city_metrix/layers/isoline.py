import geopandas as gpd
import shapely
import urllib

from .layer import Layer
from city_metrix.layers.layer import get_utm_zone_epsg

BUCKET_NAME = 'wri-cities-indicators'
PREFIX = 'data/isolines/'

class Isoline(Layer):
    def __init__(self, filename, **kwargs):
        super().__init__(**kwargs)
        # Get data from S3
        url = f'https://{BUCKET_NAME}.s3.us-east-1.amazonaws.com/{PREFIX}{filename}'
        print(f'Attempting to retrieve isoline file from {url}', end=' ')
        try:
            gdf = gpd.read_file(url)
            print('(Succeeded)')
        except urllib.error.HTTPError:
            raise Exception(f"Isoline file {filename} does not exist.")

        self.gdf = gpd.GeoDataFrame({'is_accessible': [1] * len(gdf), 'geometry': gdf.to_crs('EPSG:4326')['geometry']}).to_crs('EPSG:4326').set_crs('EPSG:4326').set_geometry('geometry')
        
    def get_data(self, bbox):
        return self.gdf.clip(shapely.box(*bbox))
