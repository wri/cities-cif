from city_metrix import *

import geopandas as gpd


def test_ttc():
    url = f"/Users/jt/Downloads/boundary-IDN-Jakarta-ADM4.geojson"
    jakarta = gpd.read_file(url)

    indicator = urban_open_space(jakarta)
    print(indicator)
