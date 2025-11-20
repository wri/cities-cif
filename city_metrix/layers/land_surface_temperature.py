import ee
import datetime, calendar
import numpy as np
from city_metrix.metrix_model import Layer, get_image_collection, GeoExtent
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 30
START_YEAR, END_YEAR = 2013, 2023

def _j2d(jdate, isleap):
    monthlengths = {
        1: 31,
        2: [28, 29][int(isleap)],
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31
    }
    sum = 0
    for month in monthlengths:
        if sum + monthlengths[month] >= jdate:
            date = jdate  - sum
            return (month, date)
        else:
            sum += monthlengths[month]

def _get_idx_date(maxtemp_idx, startyear):
    total = maxtemp_idx
    done = False
    year = startyear
    while not done:
        yearlength = [365, 366][int(calendar.isleap(year))]
        done = total - yearlength <= 0
        if not done:
            total -= yearlength
            year += 1
    date = _j2d(total, calendar.isleap(year))
    return datetime.date(year, date[0], date[1])

class LandSurfaceTemperature(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        start_date: starting date for data retrieval
        end_date: ending date for data retrieval
    """
    def _get_window(self, bbox):
        dataset = ee.ImageCollection("ECMWF/ERA5/DAILY")
        gee_geom = ee.Geometry.Point((bbox.as_geographic_bbox().centroid.coords[0][0], bbox.as_geographic_bbox().centroid.coords[0][1]))
        data_vars = dataset.select('maximum_2m_air_temperature').filter(ee.Filter.date(f'{START_YEAR}-01-01', f'{END_YEAR+1}-01-01'))
        d = data_vars.getRegion(gee_geom, DEFAULT_SPATIAL_RESOLUTION, 'epsg:4326').getInfo()
        alltemps = res = [i[4] - 273.15 for i in d[1:]]
        maxtemp = max(alltemps)
        maxtemp_idx = np.argwhere(np.array(alltemps) == maxtemp)
        maxtemp_idx
        hottest_date = _get_idx_date(int(maxtemp_idx[0][0]), START_YEAR)
        window_start = (hottest_date - datetime.timedelta(days=45))
        window_end = (hottest_date + datetime.timedelta(days=45))
        return window_start, window_end


    def __init__(self, start_date=f"{START_YEAR}-01-01", end_date=f"{END_YEAR + 1}-01-01", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date


    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

        def cloud_mask(image):
            qa = image.select('QA_PIXEL')

            mask = qa.bitwiseAnd(1 << 3).Or(qa.bitwiseAnd(1 << 4))
            return image.updateMask(mask.Not())

        def apply_scale_factors(image):
            thermal_band = image.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15)
            return thermal_band

        start_date, end_date = self._get_window(bbox)

        l8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")

        ee_rectangle = bbox.to_ee_rectangle()
        
        all_ic = ee.ImageCollection([])

        for year in range(START_YEAR, END_YEAR + 1):
            start_date_string, end_date_string = f'{year}-{start_date.strftime("%m-%d")}', f'{[year, year+1][int(start_date.month > end_date.month)]}-{end_date.strftime("%m-%d")}'
            l8_st = (l8
                     .select('ST_B10', 'QA_PIXEL')
                     .filter(ee.Filter.date(start_date_string, end_date_string))
                     .filterBounds(ee_rectangle['ee_geometry'])
                     .map(cloud_mask)
                     .map(apply_scale_factors)
                     .reduce(ee.Reducer.mean())
                     )

            l8_st_ic = ee.ImageCollection(l8_st)
            all_ic = all_ic.merge(l8_st_ic)

        data = get_image_collection(
            all_ic,
            ee_rectangle,
            spatial_resolution,
            "LST"
        ).ST_B10_mean

        return data
