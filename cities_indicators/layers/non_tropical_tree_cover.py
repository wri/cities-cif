from geopandas import GeoDataFrame
import ee


class NonTropicalTreeCover:
    NTTC = "projects/wri-datalab/cities/tree-cover/TreeCover2020-NonTropicalCitiesAug2023batch"

    def read_gee(self, gdf: GeoDataFrame):
        # read imagecollection
        ImgColl = ee.ImageCollection(self.NTTC)
        scale = ImgColl.first().projection().nominalScale()
        # reduce image collection to image
        Img = ImgColl.reduce(ee.Reducer.mean()).rename('b1')
        # clip to city extent
        data = Img.clip(ee.Geometry.BBox(*gdf.total_bounds))
        return data, scale
