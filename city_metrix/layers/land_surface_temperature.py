import ee
from datetime import datetime, timedelta
import numpy as np
from city_metrix.metrix_model import GeoExtent, Layer, get_image_collection

from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 30

class LandSurfaceTemperature(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        start_date: starting date for data retrieval
        end_date: ending date for data retrieval
    """
    def __init__(self, start_date="2013-01-01", end_date="2023-01-01", hot_season_length=None, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.hot_season_length = hot_season_length

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        # spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        spatial_resolution = self.resolution or spatial_resolution or DEFAULT_SPATIAL_RESOLUTION
        
        def get_hottest_date(bbox, start_year, end_year):
            era5_ic = ee.ImageCollection("ECMWF/ERA5/DAILY")
            centroid = ee.Geometry.Point(*list(bbox.centroid.coords), proj=bbox.crs)
            tempdata = (era5_ic
                        .filterDate(f"{start_year}-01-01", f"{end_year+1}-01-01")
                        .select("maximum_2m_air_temperature")
                        .getRegion(centroid, era5_ic.geometry().projection().nominalScale(), era5_ic.geometry().projection().crs())
                        .getInfo()
            )
            dates = [f"{i[0][:4]}-{i[0][4:6]}-{i[0][6:]}" for i in tempdata[1:]]
            temps = np.array([i[4] for i in tempdata[1:]])
            maxtemp_idx = np.argmax(temps)
            hottest_date = dates[maxtemp_idx]
            result = {
                "year": hottest_date.split("-")[0],
                "month": hottest_date.split("-")[1],
                "day": hottest_date.split("-")[2],
                }
            return result
        
        def cloud_mask(image):
            qa = image.select('QA_PIXEL')

            mask = qa.bitwiseAnd(1 << 3).Or(qa.bitwiseAnd(1 << 4))
            return image.updateMask(mask.Not())

        def apply_scale_factors(image):
            thermal_band = image.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15)
            return thermal_band

        l8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")

        now = datetime.now()

        if self.hot_season_length is not None:
            season_half_length = self.hot_season_length // 2
            hottest_date_dict = get_hottest_date(bbox, now.year-10, now.year-1)
            window_enddate = datetime.strptime(f"2002-{hottest_date_dict['month']}-{hottest_date_dict['day']}", "%Y-%m-%d") + timedelta(days=season_half_length)
            window_startdate = datetime.strptime(f"2002-{hottest_date_dict['month']}-{hottest_date_dict['day']}", "%Y-%m-%d") - timedelta(days=season_half_length)
        else:
            window_startdate = datetime.strptime(self.start_date, "%Y-%m-%d")
            window_enddate = datetime.strptime(self.end_date, "%Y-%m-%d")
        start_year_is_previous_year = window_startdate.year < window_enddate.year
        
        # Iterate through years and collect images for percentile calc
        requested_startdate = datetime.strptime(self.start_date, "%Y-%m-%d")
        requested_enddate = datetime.strptime(self.end_date, "%Y-%m-%d")

        l8_st_ic = ee.ImageCollection([])
        l8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        ee_rectangle = bbox.to_ee_rectangle()
        
        for year in range(requested_startdate.year, requested_enddate.year+1):
            startyear_adjustment = [0, 1][int(start_year_is_previous_year)]
            start_date_obj = max(requested_startdate, datetime.strptime(f"{year-startyear_adjustment}-{window_startdate.month}-{window_startdate.day}", "%Y-%m-%d"))
            start_date = start_date_obj.strftime("%Y-%m-%d")
            end_date_obj = min(requested_enddate, datetime.strptime(f"{year}-{window_enddate.month}-{window_enddate.day}", "%Y-%m-%d"))
            end_date = end_date_obj.strftime("%Y-%m-%d")
            if end_date_obj > start_date_obj:
                l8_st = (l8
                        .select('ST_B10', 'QA_PIXEL')
                        .filter(ee.Filter.date(start_date, end_date))
                        .filterBounds(ee_rectangle['ee_geometry'])
                        .map(cloud_mask)
                        .map(apply_scale_factors)
                        )

                l8_st_ic = l8_st_ic.merge(l8_st)

        mean = l8_st_ic.toBands().reduce(ee.Reducer.median()).rename('median_lst')

        data = get_image_collection(
            mean,
            ee_rectangle,
            spatial_resolution,
            "LST_median"
        ).median_lst

        return data
