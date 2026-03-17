import ee
from datetime import datetime, timedelta
import numpy as np
from city_metrix.metrix_model import GeoExtent, Layer, get_image_collection

from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 30
HOT_PERCENTILE = 95

class LandSurfaceTemperature(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        start_date: starting date for data retrieval
        end_date: ending date for data retrieval
    """
    def __init__(self, start_date="2023-01-01", end_date="2026-01-01", hot_season_length=None, use_modis=False, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.hot_season_length = hot_season_length
        self.use_modis = use_modis

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        # spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        spatial_resolution = self.resolution or spatial_resolution or DEFAULT_SPATIAL_RESOLUTION
        if self.use_modis:
            spatial_resolution = 1000

        era5_ic = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")
        coarse_era5 = ee.ImageCollection("ECMWF/ERA5/DAILY") # Using ERA5-Land at full resolution causes memory limit errors

        def get_hottest_date(bbox, start_year, end_year):
            centroid = ee.Geometry.Point(*list(bbox.centroid.coords), proj=bbox.crs)
            hottest_dates = []
            for year in range(start_year, end_year+1):
                tempdata = era5_ic.filterDate(f"{year}-01-01", f"{year+1}-01-01")
                if tempdata.size().getInfo() > 0:
                    tempdata = (tempdata
                                .select("temperature_2m_max")#("maximum_2m_air_temperature")
                                .getRegion(centroid, coarse_era5.geometry().projection().nominalScale(), coarse_era5.geometry().projection().crs())
                                .getInfo()
                    )
                    dates = [f"{i[0][:4]}-{i[0][4:6]}-{i[0][6:]}" for i in tempdata[1:]]
                    temps = np.array([i[4] for i in tempdata[1:]])
                    maxtemp_idx = np.argmax(temps)
                    hottest_date = dates[maxtemp_idx]
                    hottest_dates.append(datetime.strptime(hottest_date, "%Y-%m-%d"))
            months = [hd.month for hd in hottest_dates]
            if (1 in months) and (12 in months):
                for idx in range(len(hottest_dates)):
                    if hottest_dates[idx].month >= 10:
                        hottest_dates[idx] = hottest_dates[idx] - timedelta(days=365)
            hottest_ordinals = [d.toordinal() for d in hottest_dates]
            median_hottest_ordinal = round(np.median(hottest_ordinals))
            median_hottest = datetime.fromordinal(median_hottest_ordinal)
            
            result = {
                "year": median_hottest.year,
                "month": median_hottest.month,
                "day": median_hottest.day,
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
            hottest_date_dict = get_hottest_date(bbox, now.year-3, now.year-1)
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
        if self.use_modis:
            l8 = ee.ImageCollection("MODIS/061/MOD11A2")
        else:
            l8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        ee_rectangle = bbox.to_ee_rectangle()
        
        for year in range(requested_startdate.year, requested_enddate.year+1):
            startyear_adjustment = [0, 1][int(start_year_is_previous_year)]
            start_date_obj = max(requested_startdate, datetime.strptime(f"{year-startyear_adjustment}-{window_startdate.month}-{window_startdate.day}", "%Y-%m-%d"))
            start_date = start_date_obj.strftime("%Y-%m-%d")
            end_date_obj = min(requested_enddate, datetime.strptime(f"{year}-{window_enddate.month}-{window_enddate.day}", "%Y-%m-%d"))
            end_date = end_date_obj.strftime("%Y-%m-%d")
            if end_date_obj > start_date_obj:
                if self.use_modis:
                    l8_st = (l8
                            .select('LST_Day_1km')
                            .filter(ee.Filter.date(start_date, end_date))
                            .filterBounds(ee_rectangle['ee_geometry'])
                            .map(lambda img: img.multiply(0.02).subtract(273.15))
                            )
                else:
                    l8_st = (l8
                            .select('ST_B10', 'QA_PIXEL')
                            .filter(ee.Filter.date(start_date, end_date))
                            .filterBounds(ee_rectangle['ee_geometry'])
                            .map(cloud_mask)
                            .map(apply_scale_factors)
                            )

                l8_st_ic = l8_st_ic.merge(l8_st)

        pctl = [HOT_PERCENTILE, 50][int(self.hot_season_length is None)]
        reduced = l8_st_ic.toBands().reduce(ee.Reducer.percentile([pctl])).select(f'p{pctl}').rename(f'lst_pctl{pctl}')

        data = get_image_collection(
            reduced,
            ee_rectangle,
            spatial_resolution,
            f"LST pctl_{pctl}"
        )[f"lst_pctl{pctl}"]


        return data
