from geopandas import GeoDataFrame, GeoSeries

from city_metrix.layers import AlosDSM
from exactextract import exact_extract

def max_dsm(zones: GeoDataFrame) -> GeoSeries:
    """
    Get max AlosDSM.
    :param zones: GeoDataFrame with geometries to collect zonal stats on
    :return: Pandas Series of hights
    """
    max_height = exact_extract(AlosDSM(), zones, ["max"])

    return max_height
