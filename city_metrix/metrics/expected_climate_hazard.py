import ee
import datetime, calendar
from collections import defaultdict
import numpy as np
from geopandas import GeoDataFrame, GeoSeries
import pandas as pd
from city_metrix.layers import NexGddpCmip6
from city_metrix.constants import CSV_FILE_EXTENSION
from city_metrix.metrix_model import Metric, GeoExtent, GeoZone


VARIABLES = {
    'tas': {
        'era_varname': 'mean_2m_air_temperature',
        'nex_transform': lambda x: x - 273.5,
        'era_transform': lambda x: x - 273.5
    },
    'tasmax': {
        'era_varname': 'maximum_2m_air_temperature',
        'nex_transform': lambda x: x - 273.5,
        'era_transform': lambda x: x - 273.5
    },
    'tasmin': {
        'era_varname': 'minimum_2m_air_temperature',
        'nex_transform': lambda x: x - 273.5,
        'era_transform': lambda x: x - 273.5
    },
    'pr': {
        'era_varname': 'total_precipitation',
        'nex_transform': lambda x: x * 86400,
        'era_transform': lambda x: x * 1000
    },
}
HIST_START, HIST_END = 1980, 2014
MIN_HEATWAVE_DURATION = 3
HEATWAVE_INTENSITY_PERCENTILE = 90

def d2j(datestring):
    # Date to Julian date
    d = datetime.date.fromisoformat(datestring)
    jday = d.timetuple().tm_yday
    if calendar.isleap(d.year) and jday > 59:
        jday -= 1
    return jday

def removeLeapDays(arr, start_year, end_year, yearshift=False):
    if not yearshift:
        indices = []
        jan1_idx = 0
        for year in range(start_year, end_year+1):
            indices += [jan1_idx + i for i in range(365)]
            jan1_idx += 365
            if calendar.isleap(year):
                jan1_idx += 1
        return arr[indices]
    else:
        indices = []
        jul1_idx = 0
        for year in range(start_year-1, end_year):
            indices += [jul1_idx + i for i in range(183)]
            jul1_idx += 183
            if calendar.isleap(year):
                jul1_idx += 1
            indices += [jul1_idx + i for i in range(182)]
            jul1_idx += 182
        return arr[indices]

def summeronly(arr_noleap, southern_hem):
    if len(arr_noleap) % 365 != 0:
        raise Except('Length of input array must be integer multiple of 365')
    if southern_hem:
        include_indices = [i for i in range(len(arr_noleap)) if i % 365 >= 334 or i % 365 <= 58]
    else:
        include_indices = [i for i in range(len(arr_noleap)) if i % 365 >= 151 and i % 365 <= 242]
    return arr_noleap[include_indices]

def percentile(latlon, varname, pctl, want_summer_only=True):
    # Returns 90th percentile tasmax over 1980-2014 for June-July_Aug or Dec-Jan_Feb (if SH) for given latlon
    southern_hem = latlon[0] < 0
    dataset = ee.ImageCollection("ECMWF/ERA5/DAILY")
    era_varname = VARIABLES[varname]['era_varname']
    gee_geom = ee.Geometry.Point((latlon[1], latlon[0]))
    success = False
    retries = 0
    while not success:
        try:
            alldays = VARIABLES[varname]['era_transform'](np.array([i[4] for i in dataset.select(era_varname).filter(ee.Filter.date(f'{HIST_START}-01-01', f'{HIST_END + 1}-01-01')).getRegion(gee_geom, 27830, 'epsg:4326').getInfo()[1:]]))
            success = True
        except:
            retries += 1
            if retries >= 10:
                raise Except('Too many fetch-ERA5 retries')
    alldays_noleap = removeLeapDays(alldays, HIST_START, HIST_END, southern_hem)
    if want_summer_only:
        summer_only = summeronly(alldays_noleap, southern_hem)     
        return np.percentile(summer_only, pctl)
    else:
        return np.percentile(alldays_noleap, pctl)

def count_runs(tf_array, min_runsize):
    falses = np.zeros(tf_array.shape[0]).reshape((tf_array.shape[0],1))
    extended_a = np.concatenate([[0], tf_array, [0]])
    df = np.diff(extended_a)
    starts = np.nonzero(df == 1)[0]
    ends = np.nonzero(df == -1)[0]
    count = 0
    for idx in range(starts.size):
        if ends[idx] - starts[idx] >= min_runsize:
            count += 1
    return count

def longest_run(tf_array):
    if np.sum(tf_array) == 0:
        return 0
    falses = np.zeros(tf_array.shape[0]).reshape((tf_array.shape[0],1))
    extended_a = np.concatenate([[0], tf_array, [0]])
    df = np.diff(extended_a)
    starts = np.nonzero(df == 1)[0]
    ends = np.nonzero(df == -1)[0]
    durations = ends - starts
    return max(durations)

class Hazard:
    def __init__(self):
        self.hazname = None
    def get_expectedval(self, latlon, calib_data, start_year, end_year):
        # Take uncalibrated data, calibrate it, apply val_dist() to calibrated data, use resulting freq dist
        # to parameterize Dirichlet prior, take resulting vector to parameterize multinomial distribution,
        # sample from that multinomial to generate predictive distribution of freq distributions, and return statistics
        # (mean and stdev but it could be anything) of the predictive distribution.
        
        southern_hem = int(latlon[0] < 0)
        
        numbins = end_year - start_year + 1
        
        #calib_data = np.array(calibrate(dataset, calib_fxns))
        calib_data = np.array(calib_data)
        countdist = self.val_dist(calib_data[[0,152][int(not southern_hem)]:[len(calib_data),-213][int(not southern_hem)]])
        if countdist is None:
            para_res[modelplus] = None
        else:
            observed_vals = np.array(list(countdist.keys()))
            cdist = {}
            minval = observed_vals[0]
            maxval = observed_vals[-1]
            D = (maxval - minval) / (numbins - 1)
            for i in range(numbins):
                centerval = minval + (i * D)
                cdist[centerval] = 0
            for count in countdist:
                for centerval in cdist:
                    if count >= centerval - (D/2) and count < centerval + (D/2):
                        cdist[centerval] += 1
            alpha = np.array(list(cdist.values())) + (1/numbins)
            res = []
            for i in range(10000):
                dirich_samp = np.random.dirichlet(alpha, 1)
                mult_samp = np.random.multinomial(end_year - start_year + 1, dirich_samp[0], 1)[0]
                res.append(sum([list(cdist.keys())[j] * mult_samp[j] for j in range(len(list(cdist.keys())))]) / (end_year - start_year + 1))
            res = np.array(res)

        if res is None:
            result = -9999
        else:
            result = np.mean(res)
        return result

class Tempwave_count(Hazard):
    def __init__(self, min_duration, threshold):
        super().__init__()
        if type(threshold) == np.ndarray and threshold.size % 365 != 0:
            raise Exception('Comparison array length is not an integer multiple of 365')
        self.min_duration = min_duration
        self.threshold = threshold  # May be scalar or 365-long array

    def val_dist(self, data):
        tfarray = data >= self.threshold
        tfarray = tfarray.reshape(tfarray.size//365, 365)
        vals = np.apply_along_axis(count_runs, 1, tfarray, self.min_duration)
        
        result_dist = {}
        for val in np.unique(vals):
            result_dist[val] = np.sum(vals == val)
        return result_dist
    
class Tempwave_duration(Hazard):
    def __init__(self, threshold):
        super().__init__()
        if type(threshold) == np.ndarray and threshold.size % 365 != 0:
            raise Exception('Comparison array length is not an integer multiple of 365')
        self.threshold = threshold  # May be scalar or 365-long array

    def val_dist(self, data):
        tfarray = data >= self.threshold
        tfarray = tfarray.reshape(tfarray.size//365, 365)
        vals = np.apply_along_axis(longest_run, 1, tfarray)
        
        result_dist = {}
        for val in np.unique(vals):
            result_dist[val] = np.sum(vals == val)
        return result_dist

class ThresholdDays(Hazard):
    def __init__(self, threshold):
        self.threshold = threshold

    def val_dist(self, data):
        if data.size % 365 != 0:
            raise Exception('Data array length is not an integer multiple of 365')   
        byyear = data.reshape(data.size // 365, 365)
        
        vals = np.sum(byyear >= self.threshold, axis=1)
        result_dist = {}
        for val in np.unique(vals):
            result_dist[val] = np.sum(vals == val)
        return result_dist

class AnnualVal(Hazard):
    def __init__(self, aggtype):
        self.aggtype = aggtype
        
    def val_dist(self, data):
        byyear = data.reshape(data.size//365, 365)
        if self.aggtype == 'sum':
            vals = np.sum(byyear, axis=1)
        elif self.aggtype == 'mean':
            vals = np.mean(byyear, axis=1)
        elif self.aggtype == 'max':
            vals = np.max(byyear, axis=1)
        elif self.aggtype == 'min':
            vals = np.min(byyear, axis=1)
        result_dist = {}
        for val in np.unique(vals):
            result_dist[val] = np.sum(vals == val)
        return result_dist

class FutureHeatwaveFrequency__Heatwaves(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ['start_year', 'end_year']
    MINOR_NAMING_ATTS = ['model_rank']

    def __init__(self, start_year:int=2040, end_year:int=2049, model_rank=1, **kwargs):
        super().__init__(**kwargs)
        self.start_year = start_year
        self.end_year = end_year
        self.model_rank = model_rank
        self.unit = 'heatwaves'

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution=None
                 ) -> GeoSeries:
        
        data_layer = NexGddpCmip6(varname='tasmax', start_year=self.start_year, end_year=self.end_year)
        bbox = GeoExtent(geo_zone)
        threshold = percentile((geo_zone.centroid.y, geo_zone.centroid.x), 'tasmax', HEATWAVE_INTENSITY_PERCENTILE, True)
        haz = Tempwave_count(MIN_HEATWAVE_DURATION, threshold)
        data = data_layer.get_data(bbox)
        model = list(data.keys())[self.model_rank - 1]
        result = haz.get_expectedval((geo_zone.centroid.y, geo_zone.centroid.x), data[model], self.start_year, self.end_year)
        return pd.Series([float(round(result, 1))])

class FutureHeatwaveMaxduration__Days(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ['start_year', 'end_year']
    MINOR_NAMING_ATTS = ['model_rank']

    def __init__(self, start_year:int=2040, end_year:int=2049, model_rank=1, **kwargs):
        super().__init__(**kwargs)
        self.start_year = start_year
        self.end_year = end_year
        self.model_rank = model_rank
        self.unit = 'days'

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution=None
                 ) -> GeoSeries:

        data_layer = NexGddpCmip6(varname='tasmax', start_year=self.start_year, end_year=self.end_year)
        bbox = GeoExtent(geo_zone)
        threshold = percentile((geo_zone.centroid.y, geo_zone.centroid.x), 'tasmax', HEATWAVE_INTENSITY_PERCENTILE, True)
        haz = Tempwave_duration(threshold)
        data = data_layer.get_data(bbox)
        model = list(data.keys())[self.model_rank - 1]
        result = haz.get_expectedval((geo_zone.centroid.y, geo_zone.centroid.x), data[model], self.start_year, self.end_year)
        return pd.Series([float(round(result, 1))])

class FutureDaysAbove35__Days(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ['start_year', 'end_year']
    MINOR_NAMING_ATTS = ['model_rank']

    def __init__(self, start_year:int=2040, end_year:int=2049, model_rank=1, **kwargs):
        super().__init__(**kwargs)
        self.start_year = start_year
        self.end_year = end_year
        self.model_rank = model_rank
        self.unit = 'days'

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution=None
                 ) -> GeoSeries:

        data_layer = NexGddpCmip6(varname='tasmax', start_year=self.start_year, end_year=self.end_year)
        bbox = GeoExtent(geo_zone)
        haz = ThresholdDays(35)
        data = data_layer.get_data(bbox)
        model = list(data.keys())[self.model_rank - 1]
        result = haz.get_expectedval((geo_zone.centroid.y, geo_zone.centroid.x), data[model], self.start_year, self.end_year)
        return pd.Series([float(round(result, 1))])

class FutureAnnualMaxtemp__DegreesCelsius(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ['start_year', 'end_year']
    MINOR_NAMING_ATTS = ['model_rank']

    def __init__(self, start_year:int=2040, end_year:int=2049, model_rank=1, **kwargs):
        super().__init__(**kwargs)
        self.start_year = start_year
        self.end_year = end_year
        self.model_rank = model_rank
        self.unit = 'degrees Celsius'

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution=None
                 ) -> GeoSeries:

        data_layer = NexGddpCmip6(varname='tasmax', start_year=self.start_year, end_year=self.end_year)
        bbox = GeoExtent(geo_zone)
        haz = AnnualVal('max')
        data = data_layer.get_data(bbox)
        model = list(data.keys())[self.model_rank - 1]
        result = haz.get_expectedval((geo_zone.centroid.y, geo_zone.centroid.x), data[model], self.start_year, self.end_year)
        return pd.Series([float(round(result, 1))])

class FutureExtremePrecipitationDays__Days(Metric):
    OUTPUT_FILE_FORMAT = CSV_FILE_EXTENSION
    MAJOR_NAMING_ATTS = ['start_year', 'end_year']
    MINOR_NAMING_ATTS = ['model_rank']

    def __init__(self, start_year:int=2040, end_year:int=2049, model_rank=1, **kwargs):
        super().__init__(**kwargs)
        self.start_year = start_year
        self.end_year = end_year
        self.model_rank = model_rank
        self.unit = 'days'

    def get_metric(self,
                 geo_zone: GeoZone,
                 spatial_resolution=None
                 ) -> GeoSeries:

        data_layer = NexGddpCmip6(varname='pr', start_year=self.start_year, end_year=self.end_year)
        bbox = GeoExtent(geo_zone)
        pctl_90 = percentile((geo_zone.centroid.y, geo_zone.centroid.x), 'pr', 90, False)
        haz = ThresholdDays(pctl_90)
        data = data_layer.get_data(bbox)
        model = list(data.keys())[self.model_rank - 1]
        result = haz.get_expectedval((geo_zone.centroid.y, geo_zone.centroid.x), data[model], self.start_year, self.end_year)
        return pd.Series([float(round(result, 1))])