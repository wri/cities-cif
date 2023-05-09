import pandas as pd
import requests
import geopandas as gpd
import geemap


# read open space
def read_open_space(geo_name):

    print("load Open space data")

    # read boundary georef
    bucket_name = 'cities-cities4forests'
    aws_s3_dir = 'https://' + bucket_name + '.s3.eu-west-3.amazonaws.com/data'
    boundary_georef = pd.read_csv(aws_s3_dir + '/boundaries/v_0/boundary_georef.csv')

    # get boundary id file
    aoi_boundary_name = boundary_georef.loc[boundary_georef['geo_name'] == geo_name]['aoi_boundary_name'].iat[0]
    boundary_id_aoi = geo_name + '-' + aoi_boundary_name

    # read open space
    openspace_path = 'https://cities-cities4forests.s3.eu-west-3.amazonaws.com/data/open_space/openstreetmap/v_0/' + boundary_id_aoi + '-OSM-open_space-2022.geojson'
    openspace_geo = requests.get(openspace_path).json()
    openspace_gdf = gpd.GeoDataFrame.from_features(openspace_geo)
    openspace_geo_ee = geemap.geojson_to_ee(openspace_geo)

    return (openspace_gdf, openspace_geo_ee)