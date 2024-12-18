import ee

from .layer import Layer, get_image_collection


class AverageNetBuildingHeight(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, spatial_resolution=100, **kwargs):
        super().__init__(**kwargs)
        self.spatial_resolution = spatial_resolution

    def get_data(self, bbox):
        # https://ghsl.jrc.ec.europa.eu/ghs_buH2023.php
        # ANBH is the average height of the built surfaces, USE THIS
        # AGBH is the amount of built cubic meters per surface unit in the cell
        # US - ee.ImageCollection("projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_R2023A")
        # GLOBE - ee.Image("projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_GLOBE_R2023A")

        anbh = ee.Image("projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_GLOBE_R2023A")

        anbh_ic = ee.ImageCollection(anbh)
        data = get_image_collection(
            anbh_ic,
            bbox,
            self.spatial_resolution,
            "average net building height"
        ).b1

        return data
