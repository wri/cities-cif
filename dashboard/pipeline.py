from dashboard.carto import export_results
from dashboard.city import get_city_admin


def get_city_indicators(cities, indicators):
    """
    Run indicators on cities geometries from API and upload to carto.

    :param cities: List of city IDs
    :param indicators: List of indicator functitons
    :return: GeoDataFrame of city geometries with indicator values
    """

    ##  TODO get running

    results = []

    for city_id in cities:
        city = get_city_admin(city_id)
        for indicator in indicators:
            gdf = city.get_geom()
            results.append(indicator(gdf))


    export_results(results)

    raise NotImplementedError()