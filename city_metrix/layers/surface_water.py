import ee
import numpy as np
from scipy.signal import find_peaks
import xarray as xr

from city_metrix.metrix_model import Layer, get_image_collection, GeoExtent
from city_metrix.layers import NdwiSentinel2
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 10

class SurfaceWater(Layer):
    """"
    return: a rioxarray-format DataArray
    1 if surface water, nan otherwise
    Based on Minimum Threshold method in https://doi.org/10.1117/1.JRS.13.044507

    """
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        year: The satellite imaging year.
    """
    def __init__(self, year=2021, **kwargs):
        super().__init__(**kwargs)
        self.year = year

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        ndwi_data = NdwiSentinel2(year=self.year).get_data(bbox)

        counts, edges = np.histogram(ndwi_data, bins=1000, range=None, density=None, weights=None)
        data_y = counts.astype(float)
        data_x = (edges[:-1] + edges[1:]) / 2

        # Repeatedly smooth using 3-kernel averaging until there are two local minima
        # See Minimum Value Threshold https://doi.org/10.1117/1.JRS.13.044507
        KERNEL_SIZE = 3
        def smooth(data):
            kernel = np.ones(KERNEL_SIZE) / KERNEL_SIZE
            convolved = np.convolve(data, kernel, mode='same')

            return convolved[1:-1]
        
        while len(find_peaks(data_y)[0]) > 2:
            data_y = smooth(data_y)
            data_x = smooth(data_x)

        peaks = find_peaks(data_y)[0]
        interval = data_y[peaks[0]:peaks[1]+1]
        thresh_density = np.argwhere(data_y == np.min(interval))
        threshold = float(data_x[thresh_density[0][0]])

        data = xr.where(ndwi_data >= threshold, 1, np.nan).assign_attrs(ndwi_data.attrs)

        return data
