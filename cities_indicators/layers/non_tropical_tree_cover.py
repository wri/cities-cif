import rioxarray

from ..city import City
from ..io import read_tiles

from geopandas import GeoDataFrame
import geopandas as gpd
from shapely.geometry import box
import ee


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

    def read_gee(self, gdf: GeoDataFrame):
        # read imagecollection
        ImgColl = ee.ImageCollection(self.NTTC)
        scale = ImgColl.first().projection().nominalScale()
        # reduce image collection to image
        Img = ImgColl.reduce(ee.Reducer.mean()).rename('b1')
        # clip to city extent
        data = Img.clip(ee.Geometry.BBox(*gdf.total_bounds))
        return data, scale
