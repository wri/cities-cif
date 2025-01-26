from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_image_collection
from .layer_geometry import LayerBbox

DEFAULT_SPATIAL_RESOLUTION = 100

class AverageNetBuildingHeight(Layer):
    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, bbox: LayerBbox, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        # https://ghsl.jrc.ec.europa.eu/ghs_buH2023.php
        # ANBH is the average height of the built surfaces, USE THIS
        # AGBH is the amount of built cubic meters per surface unit in the cell
        # US - ee.ImageCollection("projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_R2023A")
        # GLOBE - ee.Image("projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_GLOBE_R2023A")

        anbh = ee.Image("projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_GLOBE_R2023A")

        ee_rectangle  = bbox.to_ee_rectangle(output_as='utm')
        anbh_ic = ee.ImageCollection(anbh)
        data = get_image_collection(
            anbh_ic,
            ee_rectangle,
            spatial_resolution,
            "average net building height"
        ).b1

        return data
