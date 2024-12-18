import ee

from .layer import Layer, get_image_collection

class TreeCanopyHeight(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    name = "tree_canopy_height"
    NO_DATA_VALUE = 0

    def __init__(self, spatial_resolution=1, **kwargs):
        super().__init__(**kwargs)
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        canopy_ht = ee.ImageCollection("projects/meta-forest-monitoring-okw37/assets/CanopyHeight")

        # aggregate time series into a single image
        canopy_ht_img = (canopy_ht
                         .reduce(ee.Reducer.mean())
                         .rename("cover_code")
                         )

        canopy_ht_ic = ee.ImageCollection(canopy_ht_img)
        data = get_image_collection(
            canopy_ht_ic,
            bbox,
            self.spatial_resolution,
            "tree canopy height"
        ).cover_code

        return data
