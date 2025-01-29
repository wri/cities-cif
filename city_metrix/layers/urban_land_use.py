from dask.diagnostics import ProgressBar
import xarray as xr
import xee
import ee

from .layer import GeoExtent, Layer, get_image_collection

DEFAULT_SPATIAL_RESOLUTION = 5

class UrbanLandUse(Layer):
    """
    Attributes:
        band: raster band used for data retrieval
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
    """

    def __init__(self, band='lulc', **kwargs):
        super().__init__(**kwargs)
        self.band = band

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        ulu = ee.ImageCollection("projects/wri-datalab/cities/urban_land_use/V1")

        # ImageCollection didn't cover the globe
        ee_rectangle = bbox.to_ee_rectangle()
        if ulu.filterBounds(ee_rectangle['ee_geometry']).size().getInfo() == 0:
            ulu_ic = ee.ImageCollection(ee.Image
                                     .constant(0)
                                     .clip(ee_rectangle['ee_geometry'])
                                     .rename('lulc')
                                     )
        else:
            ulu_ic = ee.ImageCollection(ulu
                                     .filterBounds(ee_rectangle['ee_geometry'])
                                     .select(self.band)
                                     .reduce(ee.Reducer.firstNonNull())
                                     .rename('lulc')
                                     )

        data = get_image_collection(
            ulu_ic,
            ee_rectangle,
            spatial_resolution,
            "urban land use"
        ).lulc

        return data
