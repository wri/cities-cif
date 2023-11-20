import ee
import pandas as pd
import geemap

from cityscale.layers import boundaries
from cityscale.layers import tree_mosaic_land
from cityscale.layers import esa_world_cover

# service_account = 'cities-indicators_old@wri-gee.iam.gserviceaccount.com'
# credentials = ee.ServiceAccountCredentials(service_account, 'C:/Users/Saif.Shabou/OneDrive - World Resources Institute/Documents/cities/keys/wri-gee-358d958ce7c6.json')
# ee.Initialize(credentials)

# read tml
TreeCoverImg, TreeCovergt0, TreeDataMask = tree_mosaic_land.read_tml()

# read esa
builtup, WCprojection, esaScale = esa_world_cover.read_esa(land_class="builtup")

## Create layer with tree cover in builtup areas
builtupTreeCover = TreeCovergt0.updateMask(builtup)


#### HEA-4

# define calcuation function to get pixel counts, convert to percents and append to data frame
def Hea4CountCalcsDF(FC, DF):
    # reduce images to get vegetation and built-up pixel counts
    pixelcounts = builtupTreeCover.reduceRegions(FC, ee.Reducer.count().setOutputs(['TreeBuiltPixels']),
                                                 esaScale)  # larger scale (50+) required for large cities to avoid EE memory issues
    pixelcounts = builtup.reduceRegions(pixelcounts, ee.Reducer.count().setOutputs(['BuiltPixels']),
                                        esaScale)  # larger scale (50+) required for large cities to avoid EE memory issues
    pixelcounts = TreeDataMask.reduceRegions(pixelcounts, ee.Reducer.anyNonZero().setOutputs(['TreeDataAvailable']),
                                             esaScale)
    pixelcounts = TreeCoverImg.reduceRegions(pixelcounts, ee.Reducer.mean().setOutputs(['TreeCoverMean']), esaScale)

    # convert pixel counts to area percentages and saves to FC as property
    def toPct(feat):
        BuiltpctEq = ee.Number(1).subtract((feat.getNumber('TreeBuiltPixels')).divide(feat.getNumber('BuiltPixels')))
        Builtpct = ee.Algorithms.If(feat.getNumber('TreeDataAvailable').eq(0), "NA", BuiltpctEq)
        Treepct = ee.Algorithms.If(feat.getNumber('TreeDataAvailable').eq(0), "NA",
                                   (feat.getNumber('TreeCoverMean').multiply(0.01)))
        return feat.set({
            'PctBuiltwoTree': Builtpct,
            'PctTreeCover': Treepct
        })

    pixelcounts = pixelcounts.map(toPct).select(['geo_id', 'PctBuiltwoTree', 'PctTreeCover'])

    # store in df and append
    df = geemap.ee_to_pandas(pixelcounts)
    df = df.rename(columns={'PctBuiltwoTree': 'GRE_1_4_percentBuiltupWithoutTreeCover'})
    DF = DF.append(df)
    return DF


# define calculation function to get pixel counts, convert to percents and append to data frame
def ComputeHea4(cities):
    indicator_df = pd.DataFrame()
    indicator_geo = pd.DataFrame()

    print('compute indicator HEA-4')

    for i in range(0, len(cities)):
        city = cities[i]
        print(city)

        print("process aoi level")
        boundary_geo, boundary_geo_ee = boundaries.read_boundary(geo_name=city, admin_level='aoi')
        indicator_df = Hea4CountCalcsDF(boundary_geo_ee, indicator_df)
        # merge with geo
        indicator_geo_aoi = boundary_geo.merge(indicator_df, on='geo_id', how='left')
        # append
        indicator_geo = pd.concat([indicator_geo, indicator_geo_aoi], ignore_index=True)

        print("process unit level")
        boundary_geo, boundary_geo_ee = boundaries.read_boundary(geo_name=city, admin_level='unit')
        indicator_df = Hea4CountCalcsDF(boundary_geo_ee, indicator_df)
        # merge with geo
        indicator_geo_unit = boundary_geo.merge(indicator_df, on='geo_id', how='left')
        # append
        indicator_geo = pd.concat([indicator_geo, indicator_geo_unit], ignore_index=True)

    return indicator_df, indicator_geo


# Test

# indicator_df, indicator_geo = ComputeHea4(cities = ['BRA-Salvador'])
#
# print(indicator_df)