import ee

from .layer import Layer, get_image_collection


class NasaDEM(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, spatial_resolution=30, **kwargs):
        super().__init__(**kwargs)
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        nasa_dem = ee.Image("NASA/NASADEM_HGT/001")

        nasa_dem_elev = (ee.ImageCollection(nasa_dem)
                         .filterBounds(ee.Geometry.BBox(*bbox))
                         .select('elevation')
                         .mean()
                         )

        nasa_dem_elev_ic = ee.ImageCollection(nasa_dem_elev)
        data = get_image_collection(
            nasa_dem_elev_ic,
            bbox,
            self.spatial_resolution,
            "NASA DEM"
        ).elevation

        return data
