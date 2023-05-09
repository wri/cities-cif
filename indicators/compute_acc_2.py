import ee
import pandas as pd
import geemap

from cityscale.layers import boundaries
from cityscale.layers import esa_world_cover
from cityscale.layers import open_space

# read esa
esa_land_cover, WCprojection, esaScale = esa_world_cover.read_esa(land_class="all")


# Function to translate pixel counts into area and percents
def CountToArea(feat):
    feat = ee.Feature(feat)
    FeatArea = ee.Number(feat.area(1)).multiply(0.000001)
    UrbanOpenArea = ee.Number(feat.getNumber('UrbanOpenPixels')).multiply(ee.Number(100)).multiply(ee.Number(0.000001))
    BuiltupArea = ee.Number(feat.getNumber('BuiltupPixels')).multiply(ee.Number(100)).multiply(ee.Number(0.000001))
    OpenAreaPctofBuiltUpArea = ee.Number(UrbanOpenArea).divide(ee.Number(BuiltupArea))

    return feat.set({
        'OpenAreaPctofBuiltUpArea': OpenAreaPctofBuiltUpArea,
    })

## define scale for reductions - 10 is ideal, but can be increased if memory errors with large geographies
Scale = 10

# compute acc-2

def ComputeAcc2(cities):
    indicator_df = pd.DataFrame()
    indicator_geo = pd.DataFrame()

    print('compute indicator ACC-2')

    for i in range(0, len(cities)):
        city = cities[i]
        print(city)

        print("process aoi level")

        # read open space
        openspace_geo, openspace_geo_ee = open_space.read_open_space(geo_name=city)

        # Make an image, with the same projection as WorldCover, out of the OSM ways in the FC.
        RecSitesImg = openspace_geo_ee.style(
            color='gray',
        ).reproject(
            crs=WCprojection
        )

        # create image with two bands: BuiltupPixels and UrbanOpenPixels
        Builtup = esa_land_cover.updateMask(esa_land_cover.eq(50)).rename("BuiltupPixels")
        UrbanOpen = RecSitesImg.updateMask(esa_land_cover.eq(50)).select(1).rename("UrbanOpenPixels")
        comb = Builtup.addBands([UrbanOpen])


        # read boundary
        boundary_geo, boundary_geo_ee = boundaries.read_boundary(geo_name=city, admin_level='aoi')

        # create FeatureCollection with pixels counts of Builtup and UrbanOpen for each feature
        OpenBuiltcount = comb.reduceRegions(
            reducer=ee.Reducer.count(),
            collection=boundary_geo_ee,
            scale=Scale,
            tileScale=1
        )

        # apply CountToArea function to FeatureCollection
        OpenBuiltAreaPct = OpenBuiltcount.map(CountToArea).select(['geo_id', 'OpenAreaPctofBuiltUpArea'])

        # store in df and apend
        df = geemap.ee_to_pandas(OpenBuiltAreaPct)
        df = df.rename(columns={"OpenAreaPctofBuiltUpArea": "GRE_3_1_percentOpenSpaceinBuiltup"})
        indicator_df = indicator_df.append(df)

        # merge with geo
        indicator_geo_aoi = boundary_geo.merge(indicator_df, on='geo_id', how='left')
        # append
        indicator_geo = pd.concat([indicator_geo, indicator_geo_aoi], ignore_index=True)

        print("process unit level")

        boundary_geo, boundary_geo_ee = boundaries.read_boundary(geo_name=city, admin_level='unit')

        # create FeatureCollection with pixels counts of Builtup and UrbanOpen for each feature
        OpenBuiltcount = comb.reduceRegions(
            reducer=ee.Reducer.count(),
            collection=boundary_geo_ee,
            scale=Scale,
            tileScale=1
        )

        # apply CountToArea function to FeatureCollection
        OpenBuiltAreaPct = OpenBuiltcount.map(CountToArea).select(['geo_id', 'OpenAreaPctofBuiltUpArea'])

        # store in df and apend
        df = geemap.ee_to_pandas(OpenBuiltAreaPct)
        df = df.rename(columns={"OpenAreaPctofBuiltUpArea": "GRE_3_1_percentOpenSpaceinBuiltup"})
        indicator_df = indicator_df.append(df)

        # merge with geo
        indicator_geo_aoi = boundary_geo.merge(indicator_df, on='geo_id', how='left')
        # append
        indicator_geo = pd.concat([indicator_geo, indicator_geo_aoi], ignore_index=True)


    return indicator_df, indicator_geo



# test
# indicator_df, indicator_geo = ComputeAcc2(cities = ['BRA-Salvador'])
#
# print(indicator_df)
# print(indicator_geo)