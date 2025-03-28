from city_metrix.layers import FractionalVegetation
from geopandas import GeoDataFrame, GeoSeries

def percent_area_fracveg_exceeds_threshold(zones: GeoDataFrame, threshold:float=0.6, year=2024) -> GeoSeries:
    fracveg_all_layer = FractionalVegetation(min_threshold=None, year=year)
    fracveg_gte_thresh_layer = FractionalVegetation(min_threshold=threshold, year=year)
    return fracveg_gte_thresh_layer.groupby(zones).sum() / fracveg_all_layer.groupby(zones).count()