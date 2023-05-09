import ee
import pandas as pd
import requests
import geopandas as gpd


# read boundaries
def read_boundary(geo_name, admin_level):
    # read boundary georef
    bucket_name = 'cities-cities4forests'
    aws_s3_dir = 'https://' + bucket_name + '.s3.eu-west-3.amazonaws.com/data'
    boundary_georef = pd.read_csv(aws_s3_dir + '/boundaries/v_0/boundary_georef.csv')

    if (admin_level == "aoi"):
        print('aoi level')
        aoi_boundary_name = boundary_georef.loc[boundary_georef['geo_name'] == geo_name]['aoi_boundary_name'].iat[0]
        boundary_path = aws_s3_dir + '/boundaries/v_0/boundary-' + geo_name + '-' + aoi_boundary_name + '.geojson'
    elif (admin_level == "unit"):
        unit_boundary_name = boundary_georef.loc[boundary_georef['geo_name'] == geo_name]['units_boundary_name'].iat[0]
        boundary_path = aws_s3_dir + '/boundaries/v_0/boundary-' + geo_name + '-' + unit_boundary_name + '.geojson'

    boundary_geo = requests.get(boundary_path).json()
    boundary_geo_ee = ee.FeatureCollection(boundary_geo)
    boundary_gdf = gpd.GeoDataFrame.from_features(boundary_geo)

    return (boundary_gdf, boundary_geo_ee)