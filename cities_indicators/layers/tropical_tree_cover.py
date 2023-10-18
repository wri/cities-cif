import rioxarray

from cities_indicators.city import City
from cities_indicators.io import read_tiles, read_gee

from geopandas import GeoDataFrame
import geopandas as gpd
from shapely.geometry import box


class TropicalTreeCover:
    EXTENTS_URI = "gs://gee-exports/tropical-tree-cover/2020/tropical-tree-cover-2020-extents.geojson"
    NO_DATA_VALUE = -99
    TML = "projects/wri-datalab/TropicalTreeCover"

    def read(self, gdf: GeoDataFrame, snap_to=None):
        extents = gpd.read_file(self.EXTENTS_URI)
        bbox = box(*gdf.total_bounds)

        intersecting_extents = extents[extents.intersects(bbox)]
        centroid_extent = intersecting_extents[intersecting_extents.intersects(bbox.centroid)].geometry.iloc[0]
        final_extents = intersecting_extents[~intersecting_extents.overlaps(centroid_extent)]

        data = read_tiles(gdf, final_extents.uri.to_list(), snap_to, no_data=self.NO_DATA_VALUE)
        return data

    def read_from_gee(self, gdf: GeoDataFrame):
        data = read_gee(gdf, self.TML)
        return data
