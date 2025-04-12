# File defines bboxes using in the test code
from city_metrix.layers.layer import WGS_CRS
from city_metrix.layers.layer_geometry import GeoExtent, construct_city_aoi_json
from city_metrix.metrics.metric_geometry import GeoZone

BBOX_BRA_LAURO_DE_FREITAS_1 = GeoExtent(
    bbox=(-38.35530428121955, -12.821710300686393, -38.33813814352424, -12.80363249765361), crs=WGS_CRS
)

BBOX_BRA_SALVADOR_ADM4 = GeoExtent(
    bbox=(-38.647320153390055, -13.01748678217598787, -38.3041637148564007, -12.75607703449720631), crs=WGS_CRS
)

# UTM Zones 22S and 23S
BBOX_BRA_BRASILIA = GeoExtent(bbox=(-48.07651, -15.89788, -47.83736, -15.71919), crs=WGS_CRS)

BBOX_SMALL = GeoExtent(bbox=(-38.43864, -12.97987, -38.39993, -12.93239), crs=WGS_CRS)

BBOX_NLD_AMSTERDAM = GeoExtent(bbox=(4.9012, 52.3720, 4.9083, 52.3752), crs=WGS_CRS)

BBOX_NLD_AMSTERDAM_LARGE = GeoExtent(
    bbox=(4.884629880473071, 52.34146514406914, 4.914180290924863, 52.359560786247165), crs=WGS_CRS
)

BBOX_USA_OR_PORTLAND = GeoExtent(bbox=(-122.7037, 45.51995, -122.6923117, 45.5232773), crs=WGS_CRS)
BBOX_USA_OR_PORTLAND_1 = GeoExtent(bbox=(-122.68096, 45.49394, -122.66703, 45.50139), crs=WGS_CRS)
BBOX_USA_OR_PORTLAND_2 = GeoExtent(bbox=(-122.75020, 45.58043, -122.73720, 45.58910), crs=WGS_CRS)

BBOX_IDN_JAKARTA = GeoExtent(bbox=(106.7, -6.3, 106.8, -6.2), crs=WGS_CRS)
BBOX_IDN_JAKARTA_LARGE = GeoExtent(bbox=(106, -7, 107, -6), crs=WGS_CRS)

BBOX_IND_BHOPAL = GeoExtent(bbox=(77.41791, 23.20914, 77.42856, 23.21651), crs=WGS_CRS)

# Saif recommended Teresina since it's small and has all layers available
geo_extent = construct_city_aoi_json("BRA-Florianopolis", "city_admin_level")
GEOEXTENT_MEDIUM_CITY_WGS84 = GeoExtent(bbox=geo_extent)
GEOEXTENT_MEDIUM_CITY_UTM = GeoExtent(bbox=geo_extent, crs='EPSG:32722')

geo_extent = construct_city_aoi_json("BRA-Teresina", "city_admin_level")
GEOEXTENT_SMALL_CITY_WGS84 = GeoExtent(bbox=geo_extent)
GEOEXTENT_SMALL_CITY_UTM = GeoExtent(bbox=geo_extent, crs='EPSG:32722')

geo_zone = construct_city_aoi_json("BRA-Teresina", "city_admin_level")
GEOZONE_SMALL_CITY_WGS84 = GeoZone(geo_zone=geo_zone)

