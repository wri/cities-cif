from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import VegetationWaterMap


def vegetation_water_change(zones: GeoDataFrame) -> GeoSeries:
    for i in range(len(zones)):
        veg_water_map = VegetationWaterMap().get_data(zones.iloc[[i]].total_bounds)

    counts = vegwaterImg.select('startgreenwaterIndex').reduceRegions(collection=boundary,reducer=ee.Reducer.count().setOutputs(['greenorwater2018']),scale=30)#,tileScale=10)
    counts = vegwaterImg.select('lossgreenwaterSlope').reduceRegions(collection=counts,reducer=ee.Reducer.count().setOutputs(['greenorwaterLoss']),scale=30)#,tileScale=10)
    counts = vegwaterImg.select('gaingreenwaterSlope').reduceRegions(collection=counts,reducer=ee.Reducer.count().setOutputs(['greenorwaterGain']),scale=30)#,tileScale=10)

    return 
