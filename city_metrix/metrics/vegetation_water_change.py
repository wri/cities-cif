from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import VegetationWaterMap
from city_metrix.metrics.metric import Metric

# TODO: layer generation and zonal stats use different spatial resolutions

class VegetationWaterChangeGainArea(Metric):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 zones: GeoDataFrame, spatial_resolution=10) -> GeoSeries:

        gain_counts = VegetationWaterMap(greenwater_layer='gaingreenwaterSlope').groupby(zones).count()
        gain_area = gain_counts * spatial_resolution ** 2

        return gain_area


class VegetationWaterChangeLossArea(Metric):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 zones: GeoDataFrame, spatial_resolution=10) -> GeoSeries:

        loss_counts = VegetationWaterMap(greenwater_layer='lossgreenwaterSlope').groupby(zones).count()
        loss_area = loss_counts * spatial_resolution ** 2

        return loss_area


class VegetationWaterChangeGainLossRatio(Metric):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self,
                 zones: GeoDataFrame) -> GeoSeries:

        start_counts = VegetationWaterMap(greenwater_layer='startgreenwaterIndex').groupby(zones).count()
        loss_counts = VegetationWaterMap(greenwater_layer='lossgreenwaterSlope').groupby(zones).count()
        gain_counts = VegetationWaterMap(greenwater_layer='gaingreenwaterSlope').groupby(zones).count()

        return (gain_counts - loss_counts) / start_counts
