import shapely
import math
import xarray as xr
import rioxarray
import numpy as np
from osgeo import gdal
from pyproj import CRS

from city_metrix.constants import GTIFF_FILE_EXTENSION
from city_metrix.metrix_model import Layer, GeoExtent
from .world_pop import WorldPop, WorldPopClass
from .urban_land_use import UrbanLandUse

BUCKET_NAME = 'wri-cities-indicators'
PREFIX = 'devdata/inputdata/isochrones'
DEFAULT_SPATIAL_RESOLUTION = 100
INFORMAL_CLASS = 3
SUPPORTED_AMENITIES = ('commerce', 'economic', 'healthcare',
                       'openspace', 'schools', 'transit')


def _no_overlap(ref_array, data_array):
    if (not 'y' in ref_array.dims) or (not 'x' in ref_array.dims):
        return True
    if min(ref_array.x) > max(data_array.x):
        return True
    if max(ref_array.x) < min(data_array.x):
        return True
    if min(ref_array.y) > max(data_array.y):
        return True
    if max(ref_array.y) < min(data_array.y):
        return True
    return False


def _get_aligned_dataarray(ref_array, data_array):
    # returns DataArray with data from data_array, but with shape and coords from ref_array
    # ref_array, data_array will be count_data, population_data
    # ref_array must fit geographically within data_array
    # ref_array and data_array must have same resolution
    # dims must be y, x

    if _no_overlap(ref_array, data_array):
        res = ref_array.where(True, np.nan)
        return res

    if ref_array.y[0] > ref_array.y[-1]:
        if data_array.y[0] < data_array.y[-1]:
            data_array = data_array.reindex(y=data_array.y[::-1])    

    first_corner = data_array.sel(
        x=ref_array.x[0], y=ref_array.y[0], method='nearest')
    x0 = first_corner.x.data.tolist()
    y0 = first_corner.y.data.tolist()
    x0_idx = list(data_array.x).index(x0)
    y0_idx = list(data_array.y).index(y0)

    return data_array[y0_idx:y0_idx + ref_array.shape[0], x0_idx:x0_idx + ref_array.shape[1]]


class AccessibleCount(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["project"]
    MINOR_NAMING_ATTS = ["amenity", "city_id",
                         "level", "travel_mode", "threshold", "unit"]

    def __init__(self, amenity='economic', city_id='BRA-Teresina', level='adminbound', travel_mode='walk', threshold=15, unit='minutes', project=None, **kwargs):
        super().__init__(**kwargs)
        self.city_id = city_id
        self.level = level
        self.amenity = amenity
        self.travel_mode = travel_mode
        self.threshold = threshold
        self.unit = unit
        self.project = project

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_cache_retrieval=False):
        if self.project is not None:
            project_tag = '__' + self.project
        else:
            project_tag = ''

        url = f'https://{BUCKET_NAME}.s3.us-east-1.amazonaws.com/{PREFIX}/{self.amenity}__{self.city_id}__{self.level}__{self.travel_mode}__{self.threshold}__{self.unit}{project_tag}.tif'
        print(f'Attempting to retrieve accessibility file from {url}', end=' ')
        try:
            ds = rioxarray.open_rasterio(url)
            print('(Succeeded)')
        except:
            raise Exception(f"Accessibility file {url} does not exist.")
        # ds0 = gdal.Open(url)
        # crs = CRS.from_string(ds0.GetProjection())
        # #ds.rio.write_crs(crs.to_string(), inplace=True)
        # ds.rio.write_crs(bbox.as_utm_bbox().crs, inplace=True)
        
        # ds_clipped = ds.rio.clip([shapely.box(*bbox.as_utm_bbox().coords)], all_touched=True, drop=False).squeeze()

        bbox_box = shapely.box(*bbox.as_utm_bbox().coords)
        ds_box = shapely.box(float(min(ds.x)), float(min(ds.y)), float(max(ds.x)), float(max(ds.y)))
        if shapely.intersects(bbox_box, ds_box):
            print(ds)
            print(ds.dims)
            result = ds.rio.clip_box(*bbox.as_utm_bbox().coords, allow_one_dimensional_raster=True).squeeze(['band'])
        else:
            coords= {
                'y': np.arange(bbox.bbox[1], bbox.bbox[3] + spatial_resolution, spatial_resolution),
                'x': np.arange(bbox.bbox[0], bbox.bbox[2] + spatial_resolution, spatial_resolution)
            }
            values = np.zeros(shape=(len(coords['y']), len(coords['x'])), dtype=np.uint8)

            result = xr.DataArray(values, coords).rio.write_crs(bbox.as_utm_bbox().crs)
        return result


class AccessibleRegion(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["amenity", "city_id",
                         "level", "travel_mode", "threshold", "unit"]
    MINOR_NAMING_ATTS = None

    def __init__(self, amenity='economic', city_id='BRA-Teresina', level='adminbound', travel_mode='walk', threshold=15, unit='minutes', project=None, **kwargs):
        super().__init__(**kwargs)
        self.city_id = city_id
        self.level = level
        self.amenity = amenity
        self.travel_mode = travel_mode
        self.threshold = threshold
        self.unit = unit
        self.project = project

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_cache_retrieval=False):
        accessible_count = AccessibleCount(amenity=self.amenity, city_id=self.city_id, level=self.level,
                                           travel_mode=self.travel_mode, threshold=self.threshold, unit=self.unit, project=self.project).get_data(bbox)
        ds = xr.where(accessible_count > 0, 1, np.nan, True)
        ds.rio.write_crs(bbox.as_utm_bbox().crs, inplace=True).squeeze()

        return ds


class AccessibleCountPopWeighted(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["amenity", "city_id", "level", "travel_mode", "threshold",
                         "unit", "worldpop_agesex_classes", "worldpop_year", "informal_only"]
    MINOR_NAMING_ATTS = None

    def __init__(self, amenity='jobs', city_id='BRA-Teresina', level='adminbound', travel_mode='walk', threshold=15, unit='minutes', project=None, worldpop_agesex_classes=[], worldpop_year=2020, informal_only=False, **kwargs):
        super().__init__(**kwargs)
        self.city_id = city_id
        self.level = level
        self.amenity = amenity
        self.travel_mode = travel_mode
        self.threshold = threshold
        self.unit = unit
        self.project = project
        self.worldpop_agesex_classes = worldpop_agesex_classes
        self.worldpop_year = worldpop_year
        self.informal_only = informal_only

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None, allow_cache_retrieval=False):
        utm_crs = bbox.as_utm_bbox().crs
        population_layer = WorldPop(
            agesex_classes=self.worldpop_agesex_classes, year=self.worldpop_year)
        if self.informal_only:
            informal_layer = UrbanLandUse(return_value=INFORMAL_CLASS)
            population_layer.masks.append(informal_layer)

        population_data = population_layer.get_data(bbox.buffer_utm_bbox(500), spatial_resolution=DEFAULT_SPATIAL_RESOLUTION)
        count_layer = AccessibleCount(amenity=self.amenity, city_id=self.city_id, level=self.level,
                                      travel_mode=self.travel_mode, threshold=self.threshold, unit=self.unit, project=self.project)
        count_data = count_layer.get_data(
            bbox, spatial_resolution=DEFAULT_SPATIAL_RESOLUTION).fillna(0)

        aligned_population_data = _get_aligned_dataarray(
            count_data, population_data)

        count_array = count_data.to_numpy()
        population_array = aligned_population_data.to_numpy()

        numerator = xr.DataArray(count_array * population_array,
                                 dims=['y', 'x'], coords={'y': count_data.y, 'x': count_data.x})
        result = numerator / np.nanmean(population_array)
        result.rio.write_crs(utm_crs, inplace=True)

        return result
