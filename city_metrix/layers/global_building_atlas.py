import ee
import geemap
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon, box

from city_metrix.metrix_model import Layer, WGS_CRS, GeoExtent
from ..constants import GEOJSON_FILE_EXTENSION

GBA_FOLDER = 'projects/earthengine-legacy/assets/projects/sat-io/open-datasets/GLOBAL_BUILDING_ATLAS'


class GlobalBuildingAtlas(Layer):
    OUTPUT_FILE_FORMAT = GEOJSON_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    """
    Global Building Atlas (GBA) building footprints with height estimates.
    Source: https://gee-community-catalog.org/projects/gba/
    Tiles are stored per 5°x5° grid cell under:
      projects/sat-io/open-datasets/GLOBAL_BUILDING_ATLAS/{tile_id}
    Tile naming: e030_n25_e035_n20  (e/w + lon, n/s + lat, repeated for second corner)
    Feature properties: id, bbox, height, region, source, var
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox: GeoExtent, spatial_resolution=None, resampling_method=None,
                 force_data_refresh=False):
        # Note: spatial_resolution and resampling_method arguments are ignored.

        utm_crs = bbox.as_utm_bbox().crs
        geo_bbox = bbox.as_geographic_bbox()
        bbox_shape = box(geo_bbox.min_x, geo_bbox.min_y, geo_bbox.max_x, geo_bbox.max_y)

        # Find which GBA tiles intersect the bbox
        intersecting_tiles = _find_intersecting_tiles(bbox_shape)

        if not intersecting_tiles:
            building = _empty_gdf()
            building.crs = WGS_CRS
            return building

        # Load and merge all intersecting tiles, filtered to bbox
        ee_rectangle = bbox.to_ee_rectangle()
        collections = [
            ee.FeatureCollection(tile).filterBounds(ee_rectangle["ee_geometry"])
            for tile in intersecting_tiles
        ]
        merged = ee.FeatureCollection(collections).flatten()

        try:
            building = geemap.ee_to_gdf(merged).reset_index()
        except Exception:
            building = _empty_gdf()
            building.crs = WGS_CRS

        building = _clean_geometry_collection(building)

        if len(building) > 0 and building.crs.srs == WGS_CRS:
            building = building.to_crs(utm_crs)

        return building


def _parse_tile_bounds(tile_name):
    """Parse a GBA tile name (e.g. 'e030_n25_e035_n20') into (minx, miny, maxx, maxy)."""
    parts = tile_name.split('_')
    if len(parts) != 4:
        return None
    try:
        def parse_coord(s):
            val = float(s[1:])
            if s[0] in ('w', 's'):
                val = -val
            return val

        lon1 = parse_coord(parts[0])
        lat1 = parse_coord(parts[1])
        lon2 = parse_coord(parts[2])
        lat2 = parse_coord(parts[3])

        return (min(lon1, lon2), min(lat1, lat2), max(lon1, lon2), max(lat1, lat2))
    except (ValueError, IndexError):
        return None


def _find_intersecting_tiles(bbox_shape):
    """List all GBA assets and return paths of tiles that intersect bbox_shape."""
    try:
        asset_list = ee.data.listAssets(GBA_FOLDER).get('assets', [])
    except Exception as e:
        raise RuntimeError(f"Failed to list GBA assets from {GBA_FOLDER}: {e}")

    intersecting = []
    for asset in asset_list:
        asset_path = asset['name']
        tile_name = asset_path.split('/')[-1]
        bounds = _parse_tile_bounds(tile_name)
        if bounds is None:
            continue
        tile_shape = box(*bounds)
        if bbox_shape.intersects(tile_shape):
            intersecting.append(asset_path)

    return intersecting


def _empty_gdf():
    return gpd.GeoDataFrame(
        pd.DataFrame(columns=["index", "geometry", "id", "height", "region", "source", "var"]),
        geometry="geometry",
    )


def _clean_geometry_collection(building):
    """Explode GeometryCollection rows into individual Polygon/MultiPolygon rows."""
    gc_building = building[building.geom_type == "GeometryCollection"].copy()
    if len(gc_building) == 0:
        return building

    gc_building["geometries"] = gc_building.apply(lambda x: [g for g in x.geometry.geoms], axis=1)
    gc_building_polygon = []
    for index, row in gc_building.iterrows():
        for geom in row["geometries"]:
            if isinstance(geom, (Polygon, MultiPolygon)):
                new_row = row.drop(["geometry", "geometries"])
                new_row["geometry"] = geom
                gc_building_polygon.append(new_row)

    building = building[building.geom_type != "GeometryCollection"]

    if gc_building_polygon:
        gc_gdf = gpd.GeoDataFrame(gc_building_polygon, geometry="geometry", crs=gc_building.crs)
        building = pd.concat([building, gc_gdf], ignore_index=True).reset_index()
    else:
        building = building.reset_index()

    return building
