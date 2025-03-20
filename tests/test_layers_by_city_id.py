import numpy as np

from city_metrix.layers import *
from tests.resources.bbox_constants import EXTENT_SMALL_CITY_WGS84, EXTENT_SMALL_CITY_UTM


def test_esa_world_cover():
    source_data = EsaWorldCover(year=2020).get_data(EXTENT_SMALL_CITY_WGS84, allow_cached_data_retrieval=False)
    assert np.size(source_data) > 0
    cacheable_data = EsaWorldCover(year=2020).get_data(EXTENT_SMALL_CITY_WGS84, allow_cached_data_retrieval=True)
    assert np.size(cacheable_data) > 0

    assert str(source_data.dimensions) == str(cacheable_data.dimensions)



# def test_nasa_dem_city_id_wgs84():
#     data = NasaDEM().get_data(EXTENT_SMALL_CITY_WGS84)
#     assert np.size(data) > 0
#
# def test_nasa_dem_city_id_utm():
#     data = NasaDEM().get_data(EXTENT_SMALL_CITY_UTM)
#     assert np.size(data) > 0

