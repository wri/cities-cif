import xarray as xr
import rioxarray
import numpy as np
from osgeo import gdal
from pyproj import CRS
import shapely
from city_metrix.constants import GTIFF_FILE_EXTENSION
from city_metrix.metrix_model import Layer, GeoExtent
from .world_pop import WorldPop, WorldPopClass
from .urban_land_use import UrbanLandUse

BUCKET_NAME = 'wri-cities-indicators'
PREFIX = 'devdata/inputdata/isochrones'
DEFAULT_SPATIAL_RESOLUTION = 100
WORLDPOP_SPATIAL_RESOLUTION = 100
INFORMAL_CLASS = 3
SUPPORTED_AMENITIES = ('commerce', 'economic', 'healthcare', 'openspace', 'schools', 'transit')

class AccessibleCount(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["amenity", "city_id", "level", "travel_mode", "threshold", "unit"]
    MINOR_NAMING_ATTS = None

    def __init__(self, amenity='economic', city_id='KEN-Nairobi', level='adminbound', travel_mode='walk', threshold=15, unit='minutes', **kwargs):
        super().__init__(**kwargs)
        self.city_id = city_id
        self.level = level
        self.amenity = amenity
        self.travel_mode = travel_mode
        self.threshold = threshold
        self.unit = unit

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_cache_retrieval=False):
        url = f'https://{BUCKET_NAME}.s3.us-east-1.amazonaws.com/{PREFIX}/{self.amenity}__{self.city_id}__{self.level}__{self.travel_mode}__{self.threshold}__{self.unit}.tif'
        print(f'Attempting to retrieve accessibility file from {url}', end=' ')
        try:
            ds = rioxarray.open_rasterio(url)
            print('(Succeeded)')
        except:
            raise Exception(f"Accessibility file {url} does not exist.")
        ds0 = gdal.Open(url)
        crs = CRS.from_string(ds0.GetProjection())
        ds.rio.write_crs(crs.to_string(), inplace=True)
        ds_clipped = ds.rio.clip_box(*bbox.as_utm_bbox().coords).squeeze()
        return ds_clipped

class AccessibleRegion(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["amenity", "city_id", "level", "travel_mode", "threshold", "unit"]
    MINOR_NAMING_ATTS = None

    def __init__(self, amenity='economic', city_id='KEN-Nairobi', level='adminbound', travel_mode='walk', threshold=15, unit='minutes', **kwargs):
        super().__init__(**kwargs)
        self.city_id = city_id
        self.level = level
        self.amenity = amenity
        self.travel_mode = travel_mode
        self.threshold = threshold
        self.unit = unit

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_cache_retrieval=False):
        accessible_count = AccessibleCount(amenity=self.amenity, city_id=self.city_id, level=self.level, travel_mode=self.travel_mode, threshold=self.threshold, unit=self.unit).get_data(bbox)
        ds = xr.where(accessible_count > 0, 1, np.nan, True)
        ds.rio.write_crs(bbox.as_utm_bbox().crs, inplace=True).squeeze()
        return ds

class AccessibleCountPopWeighted(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["amenity", "city_id", "level", "travel_mode", "threshold", "unit", "worldpop_agesex_classes", "worldpop_year", "informal_only"]
    MINOR_NAMING_ATTS = None

    def __init__(self, amenity='jobs', city_id='KEN-Nairobi', level='adminbound', travel_mode='walk', threshold=15, unit='minutes', worldpop_agesex_classes=[], worldpop_year=2020, informal_only=False, **kwargs):
        super().__init__(**kwargs)
        self.city_id = city_id
        self.level = level
        self.amenity = amenity
        self.travel_mode = travel_mode
        self.threshold = threshold
        self.unit = unit
        self.worldpop_agesex_classes = worldpop_agesex_classes
        self.worldpop_year = worldpop_year
        self.informal_only = informal_only

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=WORLDPOP_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_cache_retrieval=False):
        utm_crs = bbox.as_utm_bbox().crs
        population_layer = WorldPop(agesex_classes=self.worldpop_agesex_classes, year=self.worldpop_year)
        if self.informal_only:
            informal_layer = UrbanLandUse(return_value=INFORMAL_CLASS)
            population_layer.masks.append(informal_layer)
        population_data = population_layer.get_data(bbox, spatial_resolution=spatial_resolution)
        count_layer = AccessibleCount(amenity=self.amenity, city_id=self.city_id, level=self.level, travel_mode=self.travel_mode, threshold=self.threshold, unit=self.unit)
        count_data = count_layer.get_data(bbox, spatial_resolution=WORLDPOP_SPATIAL_RESOLUTION)
        numerator = xr.DataArray(count_data.fillna(0).to_numpy() * population_data.to_numpy(), dims=['y', 'x'], coords={'y': count_data.y, 'x': count_data.x})
        result = numerator / population_data.mean()
        result.rio.write_crs(utm_crs, inplace=True)
        return result