from city_metrix import GeoZone, GeoExtent
from city_metrix.metrix_tools import construct_city_aoi_json

# urban_extents
city_admin = construct_city_aoi_json("BRA-Teresina", "urban_extent")
GEOZONE_TERESINA_URBAN_EXTENT = GeoZone(geo_zone=city_admin)
GEOEXTENT_TERESINA_URBAN_EXTENT = GeoExtent(GEOZONE_TERESINA_URBAN_EXTENT)

city_admin = construct_city_aoi_json("BRA-Florianopolis", "urban_extent")
GEOZONE_FLORIANOPOLIS_URBAN_EXTENT = GeoZone(geo_zone=city_admin)
GEOEXTENT_FLORIANOPOLIS_URBAN_EXTENT = GeoExtent(GEOZONE_FLORIANOPOLIS_URBAN_EXTENT)

# city_admin_level
city_admin = construct_city_aoi_json("BRA-Teresina", "city_admin_level")
GEOZONE_TERESINA_CITY_ADMiN_LEVEL= GeoZone(geo_zone=city_admin)

