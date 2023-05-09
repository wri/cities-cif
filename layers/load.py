import ee
import pandas as pd
import requests
import geopandas as gpd

ee.Initialize()

# read tml data

def read_tml():
    ## read Trees in Mosaic Landscapes tree cover dataset
    TML = ee.ImageCollection('projects/wri-datalab/TML')
    TreeCoverImg = TML.reduce(ee.Reducer.mean()).rename('b1')
    TreeCovergt0 = TreeCoverImg.updateMask(TreeCoverImg.gt(0))

    TreeDataMask = TreeCoverImg.unmask(-99).neq(-99)

    return (TreeCoverImg, TreeCovergt0, TreeDataMask)



# read esa data
def read_esa(land_class):
    ##Add Land use land cover dataset
    WC = ee.ImageCollection("ESA/WorldCover/v100")
    WorldCover = WC.first()

    WCprojection = WC.first().projection()
    esaScale = WorldCover.projection().nominalScale()

    if (land_class == "all"):
        esa_data = WorldCover
    elif (land_class == "builtup"):
        esa_data = WorldCover.eq(50)

    return (esa_data, WCprojection, esaScale)


# read boundaries
def read_boundary(geo_name, admin_level):
    # read boundary georef
    bucket_name = 'cities-cities4forests'
    aws_s3_dir = 'https://' + bucket_name + '.s3.eu-west-3.amazonaws.com/data'
    boundary_georef = pd.read_csv(aws_s3_dir + '/boundaries/v_0/boundary_georef.csv')

    if (admin_level == "aoi"):
        aoi_boundary_name = boundary_georef.loc[boundary_georef['geo_name'] == geo_name]['aoi_boundary_name'].iat[0]
        boundary_path = aws_s3_dir + '/boundaries/v_0/boundary-' + geo_name + '-' + aoi_boundary_name + '.geojson'
    elif (admin_level == "unit"):
        unit_boundary_name = boundary_georef.loc[boundary_georef['geo_name'] == geo_name]['units_boundary_name'].iat[0]
        boundary_path = aws_s3_dir + '/boundaries/v_0/boundary-' + geo_name + '-' + unit_boundary_name + '.geojson'

    boundary_geo = requests.get(boundary_path).json()
    boundary_geo_ee = ee.FeatureCollection(boundary_geo)
    boundary_gdf = gpd.GeoDataFrame.from_features(boundary_geo)

    return (boundary_gdf, boundary_geo_ee)
