from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import Layer, get_utm_zone_epsg, get_image_collection

class AverageNetBuildingHeight(Layer):
    def __init__(self, scale_meters=100, **kwargs):
        super().__init__(**kwargs)
        self.scale_meters = scale_meters

    def get_data(self, bbox):
        # https://ghsl.jrc.ec.europa.eu/ghs_buH2023.php
        # ANBH is the average height of the built surfaces, USE THIS
        # AGBH is the amount of built cubic meters per surface unit in the cell
        # US - ee.ImageCollection("projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_R2023A")
        # GLOBE - ee.Image("projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_GLOBE_R2023A")

        anbh = ee.Image("projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_GLOBE_R2023A")
        data = (get_image_collection(
            ee.ImageCollection(anbh), bbox, self.scale_meters, "average net building height")
                .b1)
        
        return data
