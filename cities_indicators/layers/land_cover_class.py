from geopandas import GeoDataFrame
import ee


class LandCoverClass:
    LULC = "projects/wri-datalab/cities/SSC/LULC"

    def read_gee(self, gdf: GeoDataFrame):
        # read imagecollection
        ImgColl = ee.ImageCollection(self.LULC)
        # reduce image collection to image
        Img = ImgColl.reduce(ee.Reducer.max()).rename('b1')
        # clip to city extent
        data = Img.clip(ee.Geometry.BBox(*gdf.total_bounds))
        return data
