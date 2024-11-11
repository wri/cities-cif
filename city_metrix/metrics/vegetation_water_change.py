from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import VegetationWaterMap


def vegetation_water_change(zones: GeoDataFrame) -> GeoSeries:
    start_counts = VegetationWaterMap(greenwater_layer='startgreenwaterIndex').groupby(zones).count()
    loss_counts = VegetationWaterMap(greenwater_layer='lossgreenwaterSlope').groupby(zones).count()
    gain_counts = VegetationWaterMap(greenwater_layer='gaingreenwaterSlope').groupby(zones).count()

    # TODO: layer generation and zonal stats use different spatial resolutions

    return (gain_counts - loss_counts) / start_counts
