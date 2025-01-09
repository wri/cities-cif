import geopandas as gpd
import shapely
import boto3

from .layer import Layer, get_utm_zone_epsg

BUCKET_NAME = 'wri-cities-indicators'
PREFIX = 'data/isolines/'

class Isoline(Layer):
    def __init__(self, params, aws_profilename=None, **kwargs):
        super().__init__(**kwargs)
        # params is dict with keys cityname, amenityname, travelmode, threshold_type, threshold_value, year
        cityname = params['cityname']
        amenityname = params['amenityname']
        travelmode = params['travelmode']
        threshold_type = params['threshold_type']
        threshold_value = params['threshold_value']
        year = params['year']
        # Get list of isoline files from S3 and find the most recent file with correct cityname, amenity, etc
        if aws_profilename is None:
            session = boto3.Session()
        else:
            session = boto3.Session(profile_name=aws_profilename)
        s3 = session.client('s3')
        obj_list = s3.list_objects(Bucket=BUCKET_NAME, Prefix=PREFIX)['Contents']
        objnames = [i['Key'].replace(PREFIX, '') for i in obj_list if len(i['Key'].replace(PREFIX, '')) > 0]
        matches = [oname for oname in objnames if oname.split('.')[0].split('_')[:-1] == [cityname, amenityname, travelmode, threshold_type, str(threshold_value)]]
        if year is not None:
            matches = [oname for oname in matches if oname.split('.')[0].split('_')[-1][:4] == str(year)]
        if len(matches) == 0:
            raise Exception('No isoline file found.')
        matches.sort(key=lambda x: int(x.split('.')[0].split('_')[-1]))
        objname = matches[-1]
        
        # Get data from S3
        url = f'https://{BUCKET_NAME}.s3.us-east-1.amazonaws.com/{PREFIX}{objname}'
        gdf = gpd.read_file(url)
        self.gdf = gpd.GeoDataFrame({'is_accessible': [1] * len(gdf), 'geometry': gdf.to_crs('EPSG:4326')['geometry']}).to_crs('EPSG:4326').set_crs('EPSG:4326').set_geometry('geometry')
        
    def get_data(self, bbox):
        return self.gdf.clip(shapely.box(*bbox))
