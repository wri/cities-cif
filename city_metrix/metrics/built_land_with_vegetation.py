from geopandas import GeoDataFrame, GeoSeries
from city_metrix.layers import EsaWorldCoverClass, EsaWorldCover, NdviSentinel2

def built_land_with_vegetation(zones: GeoDataFrame) -> GeoSeries:
    """
    Get percentage of built up land (using ESA world cover) with NDVI vegetation cover.
    :param zones: GeoDataFrame with geometries to collect zonal stats on
    :return: Pandas Series of percentages
    """
    ndvi_sampling_year = 2020
    ndvi_threshold = 0.4
    built_up_land = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
    vegetation = NdviSentinel2(year=ndvi_sampling_year, ndvi_threshold=ndvi_threshold)

    built_land = built_up_land.groupby(zones).count()
    vegetation_cover_in_built_land = vegetation.mask(built_up_land).groupby(zones).count()

    fraction_vegetation_in_built_up_land = (vegetation_cover_in_built_land.fillna(0) / built_land)

    return fraction_vegetation_in_built_up_land
