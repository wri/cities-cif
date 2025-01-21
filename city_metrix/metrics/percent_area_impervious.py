from geopandas import GeoDataFrame, GeoSeries
import ee
from city_metrix.layers import Layer, ImperviousSurface


def percent_area_impervious(zones: GeoDataFrame) -> GeoSeries:
    class ImperviousSurfaceFillNA(ImperviousSurface):
        def get_data(self, bbox):
            data = super().get_data(bbox)
            return data.fillna(0)

    impervious_layer = ImperviousSurface()
    totalarea_layer = ImperviousSurfaceFillNA()
    return 100 * impervious_layer.groupby(zones).sum() / totalarea_layer.groupby(zones).count()
    
