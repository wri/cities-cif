import ee
import xarray as xr
import pandas as pd
import geopandas as gpd
from datetime import datetime
from shapely.geometry import box
from rasterio.enums import Resampling

from city_metrix.metrix_model import (Layer, get_image_collection, set_resampling_for_continuous_raster,
                                      validate_raster_resampling_method, GeoExtent)
from city_metrix.metrix_tools import is_date
from .era5_hottest_day_gee import find_hottest_day, local_date_to_utc_datetime
from ..metrix_dao import extract_bbox_aoi
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 11132
DEFAULT_RESAMPLING_METHOD = 'bilinear'
DEMO_FILE_PATH = 'https://wri-cities-heat.s3.us-east-1.amazonaws.com/ZAF-Cape_Town/raw/urbclim_cape_town_output.nc'


class AirTemperature(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None
    PROCESSING_TILE_SIDE_M = 5000

    def __init__(self, start_date: str = None, end_date: str = None, single_data: str = None,
                 seasonal_utc_offset: float = 0, sampling_local_hours: str = '', **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.single_date = single_data
        self.seasonal_utc_offset = seasonal_utc_offset
        self.sampling_local_hours = sampling_local_hours

    """
    Attributes:
        spatial_resolution: raster resolution in meters (see https://github.com/stac-extensions/raster)
        resampling_method: interpolation method used by Google Earth Engine. Valid options: ('bilinear', 'bicubic', 'nearest').
    """

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method: str = DEFAULT_RESAMPLING_METHOD):

        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        resampling_method = DEFAULT_RESAMPLING_METHOD if resampling_method is None else resampling_method
        validate_raster_resampling_method(resampling_method)
        if self.single_date:
            if not is_date(self.single_date):
                raise Exception(f"Invalid single_date: {self.single_date}")
        else:
            if not is_date(self.start_date) or not is_date(self.end_date):
                raise Exception(
                    f"Invalid date specification: start_date:{self.start_date}, end_date:{self.end_date}.")

        buffered_utm_bbox = bbox.buffer_utm_bbox(10)
        geographic_bbox = buffered_utm_bbox.as_geographic_bbox()

        geographic_centroid = geographic_bbox.centroid
        center_lon = geographic_centroid.x
        center_lat = geographic_centroid.y

        dataset_land = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY")

        if self.start_date is not None and self.end_date is not None:
            utc_times_list = find_hottest_day(center_lon, center_lat, spatial_resolution,
                                              geographic_bbox, dataset_land, self.start_date, self.end_date, self.seasonal_utc_offset)
        elif self.single_date is not None:
            utc_times_list = local_date_to_utc_datetime(datetime.strptime(
                self.single_date, '%Y-%m-%d').date(), self.seasonal_utc_offset)

        ds = xr.open_dataset(DEMO_FILE_PATH, engine="h5netcdf")
        t2m = ds['T2M']
        t2m = t2m.rio.write_crs(buffered_utm_bbox.crs, inplace=False)

        # Fake time handling
        n_times = t2m.sizes["t"]
        # Generate new hourly datetimes for 2023
        new_times = pd.date_range("2023-01-01", periods=n_times, freq="h")
        # Assign them back to the DataArray
        t2m = t2m.assign_coords(t=new_times)
        # Select March 16, 2023 at 12:00/15:00/18:00 local time (UTC+2)
        # ['2023-03-16T10:00:00', '2023-03-16T13:00:00', '2023-03-16T16:00:00']
        t2m_subset = t2m.sel(
            t=[utc_times_list[i] for i in [int(h) for h in self.sampling_local_hours.split(",")]])

        xmin, ymin, xmax, ymax = buffered_utm_bbox.bounds
        gdf = gpd.GeoDataFrame(
            geometry=[box(xmin, ymin, xmax, ymax)], crs=buffered_utm_bbox.crs)
        t2m_clip = t2m_subset.rio.clip(
            gdf.geometry, gdf.crs, drop=True, all_touched=True)
        # Convert from Kelvin to Celsius
        t2m_clip = t2m_clip - 273.15

        # Resample to desired resolution
        t2m_1m = t2m_clip.rio.reproject(
            dst_crs=t2m_clip.rio.crs,
            resolution=1,
            resampling=Resampling.bilinear
        )

        # Trim back to original AOI
        result_data = extract_bbox_aoi(t2m_1m, bbox)

        return result_data
