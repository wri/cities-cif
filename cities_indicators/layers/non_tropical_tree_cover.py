import rioxarray

from cities_indicators.city import City
from cities_indicators.io import read_tiles, read_gee

from geopandas import GeoDataFrame
import geopandas as gpd
from shapely.geometry import box


class NonTropicalTreeCover:
    NTTC = "projects/wri-datalab/cities/tree-cover/TreeCover2020-NonTropicalCitiesAug2023batch"

    # def read(self, gdf: GeoDataFrame, snap_to=None):
    #     extents = gpd.read_file(self.EXTENTS_URI)
    #     bbox = box(*gdf.total_bounds)

    #     intersecting_extents = extents[extents.intersects(bbox)]
    #     centroid_extent = intersecting_extents[intersecting_extents.intersects(bbox.centroid)].geometry.iloc[0]
    #     final_extents = intersecting_extents[~intersecting_extents.overlaps(centroid_extent)]

    #     data = read_tiles(gdf, final_extents.uri.to_list(), snap_to, no_data=self.NO_DATA_VALUE)
    #     return data

    def read_from_gee(self, gdf: GeoDataFrame):
        data = read_gee(gdf, self.NTTC)
        return data
