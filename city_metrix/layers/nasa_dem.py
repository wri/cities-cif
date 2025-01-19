from math import floor, ceil

import ee
import xee
import xarray as xr

from .layer import Layer, get_image_collection, set_resampling_for_continuous_raster, get_ee_utm_rectangle


class NasaDEM(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
        resampling_method: interpolation method used by Google Earth Engine. Default is 'bilinear'. All options are: ('bilinear', 'bicubic', None).
    """

    def __init__(self, spatial_resolution:int=30, resampling_method:str='bilinear', **kwargs):
        super().__init__(**kwargs)
        self.spatial_resolution = spatial_resolution
        self.resampling_method = resampling_method

    def get_data(self, bbox: tuple[float, float, float, float]):
        nasa_dem = ee.Image("NASA/NASADEM_HGT/001")

        min_x, min_y, max_x, max_y = bbox
        retrieval_crs = 'EPSG:32724'

        # from pyproj import Transformer
        #
        # transformer = Transformer.from_crs("EPSG:4326", retrieval_crs)
        # sw_coord = transformer.transform(min_y, min_x)
        # ne_coord = transformer.transform(max_y, max_x)
        #
        # # grid_snapped_min_x = float(floor(sw_coord[0]))-2
        # # grid_snapped_min_y = float(floor(sw_coord[1]))-2
        # # grid_snapped_max_x = float(ceil(ne_coord[0]))
        # # grid_snapped_max_y = float(ceil(ne_coord[1]))
        #
        # grid_snapped_min_x = float((sw_coord[0]))
        # grid_snapped_min_y = float((sw_coord[1]))
        # grid_snapped_max_x = float((ne_coord[0]))
        # grid_snapped_max_y = float((ne_coord[1]))

        # min_x = float(floor(min_x))
        # min_y = float(floor(min_y))
        # max_x = float(floor(max_x))
        # max_y = float(floor(max_y))


        # geom = ee.Geometry.Rectangle(
        #     [[min_x, min_y],
        #      [max_x, max_y]],
        #     retrieval_crs,
        #     geodesic=False,
        #     evenOdd=True
        # )

        # geom = ee.Geometry.Rectangle(
        #     [[grid_snapped_min_x, grid_snapped_min_y],
        #      [grid_snapped_max_x, grid_snapped_max_y]],
        #     retrieval_crs,
        #     geodesic=False,
        # )
        source_crs = 32724
        utm_ee_rectangle = get_ee_utm_rectangle(bbox, source_crs)

        nasa_dem_elev = (ee.ImageCollection(nasa_dem)
                         .filterBounds(utm_ee_rectangle)
                         .select('elevation')
                         .map(lambda x:
                              set_resampling_for_continuous_raster(x,
                                                                   self.resampling_method,
                                                                   self.spatial_resolution,
                                                                   retrieval_crs
                                                                   )
                              )
                         .mean()
                         )

        nasa_dem_elev_ic = ee.ImageCollection(nasa_dem_elev)
        data = get_image_collection(
            nasa_dem_elev_ic,
            utm_ee_rectangle,
            self.spatial_resolution,
            "NASA DEM"
        ).elevation

        return data
