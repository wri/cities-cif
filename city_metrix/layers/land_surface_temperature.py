import ee
from datetime import datetime, timedelta
import numpy as np

from city_metrix.metrix_model import Layer, get_image_collection, GeoExtent
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 30

class LandSurfaceTemperature(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ["percentile", "num_seasons"]
    MINOR_NAMING_ATTS = None

    """
    Attributes:
        start_date: starting date for data retrieval
        end_date: ending date for data retrieval
    """
    def __init__(self, percentile=50, num_seasons=5, use_hot_window=False, **kwargs):
        super().__init__(**kwargs)
        self.percentile = percentile
        self.num_seasons = num_seasons
        self.use_hot_window = use_hot_window

    def get_data(self, bbox: GeoExtent, spatial_resolution:int=DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        if resampling_method is not None:
            raise Exception('resampling_method can not be specified.')
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution

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

        
        # Define window of 90 days centered on hottest date
        now = datetime.now()

        if self.use_hot_window:
            hottest_date_dict = get_hottest_date(bbox, now.year-10, now.year-1)
            window_enddate = datetime.strptime(f"2002-{hottest_date_dict['month']}-{hottest_date_dict['day']}", "%Y-%m-%d") + timedelta(days=45)
            window_startdate = datetime.strptime(f"2002-{hottest_date_dict['month']}-{hottest_date_dict['day']}", "%Y-%m-%d") - timedelta(days=45)
            start_year_is_previous_year = window_startdate.year < window_enddate.year
            current_year_incomplete = datetime.strptime(f"{now.year}-{window_enddate.month}-{window_enddate.day}", "%Y-%m-%d") > now - timedelta(days=20)
        else:
            window_startdate = datetime.strptime(f"2002-01-01", "%Y-%m-%d")
            window_enddate = datetime.strptime(f"2002-01-01", "%Y-%m-%d")
            start_year_is_previous_year = True
            current_year_incomplete = True
        
        # Iterate through years and collect images for percentile calc
        l8_st_list = ee.List([])
        l8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        ee_rectangle = bbox.to_ee_rectangle()
        
        if current_year_incomplete:
            start_year, end_year = now.year-self.num_seasons, now.year-1
        else:
            start_year, end_year = now.year-self.num_seasons+1, now.year
        for year in range(start_year, end_year+1):
            if start_year_is_previous_year:
                start_date = f"{year-1}-{window_startdate.month}-{window_startdate.day}"
            else:
                start_date = f"{year}-{window_startdate.month}-{window_startdate.day}"
            end_date = f"{year}-{window_enddate.month}-{window_enddate.day}"

            l8_st = (l8
                    .select('ST_B10', 'QA_PIXEL')
                    .filter(ee.Filter.date(start_date, end_date))
                    .filterBounds(ee_rectangle['ee_geometry'])
                    .map(cloud_mask)
                    .map(apply_scale_factors)
                    .reduce(ee.Reducer.mean())
                    )

            l8_st_list = l8_st_list.add(l8_st)
        
        # Get 95th (or other) percentile of collected images, pixelwise
        pctl = ee.ImageCollection(l8_st_list).toBands().reduce(ee.Reducer.percentile([self.percentile]))
        data = get_image_collection(
                pctl,
                ee_rectangle,
                spatial_resolution,
                f"LST_percentile_{self.percentile}"
            )[f"p{self.percentile}"]

        return data
