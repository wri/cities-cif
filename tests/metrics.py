from city_metrix import tree_cover, high_land_surface_temperature

import geopandas as gpd


def test_ttc():
    url = f"/Users/jt/Downloads/boundary-IDN-Jakarta-ADM4.geojson"
    jakarta = gpd.read_file(url)

    indicator = high_land_surface_temperature(jakarta)
    print(indicator)
