import datetime
import calendar
import math
import ee
import numpy as np
from enum import Enum

from city_metrix.metrix_model import Layer, get_image_collection, GeoExtent
from ..constants import GTIFF_FILE_EXTENSION

DEFAULT_SPATIAL_RESOLUTION = 27830

MODEL_INFO = {'UKESM1-0-LL': 'HadAM',
              'NorESM2-MM': 'CCM',
              'NorESM2-LM': 'CCM',
              'MRI-ESM2-0': 'UCLA GCM',
              'MPI-ESM1-2-LR': 'ECMWF',
              'MPI-ESM1-2-HR': 'ECMWF',
              'MIROC6': 'MIROC',
              'MIROC-ES2L': 'MIROC',
              'KIOST-ESM': 'GFDL',
              'KACE-1-0-G': 'HadAM',
              'IPSL-CM6A-LR': 'IPSL',
              'INM-CM5-0': 'INM',
              'INM-CM4-8': 'INM',
              'HadGEM3-GC31-MM': 'HadAM',
              'HadGEM3-GC31-LL': 'HadAM',
              'GFDL-ESM4': 'GFDL',
              'GFDL-CM4_gr2': 'GFDL',
              'GFDL-CM4': 'GFDL',
              'FGOALS-g3': 'CCM',
              'EC-Earth3-Veg-LR': 'ECMWF',
              'EC-Earth3': 'ECMWF',
              'CanESM5': 'CanAM',
              'CNRM-ESM2-1': 'ECMWF',
              'CNRM-CM6-1': 'ECMWF',
              'CMCC-ESM2': 'CCM',
              'CMCC-CM2-SR5': 'CCM',
              'BCC-CSM2-MR': 'CCM',
              'ACCESS-ESM1-5': 'HadAM',
              'ACCESS-CM2': 'HadAM',
              'TaiESM1': 'CCM',
              }
EXCLUDED_MODELS = ['GFDL-CM4_gr2', 'ERA5']
HURS_EXCLUDED = ['BCC-CSM2-MR', 'NESM3', 'KIOST-ESM']
HUSS_EXCLUDED = ['IPSL-CM6A-LR', 'MIROC6', 'NESM3']
MODELS = [i for i in MODEL_INFO if not i in EXCLUDED_MODELS]
HIST_START = 1980
HIST_END = 2014


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


def hurs_era(latlon, start_year=HIST_START, end_year=HIST_END, yearshift=False, scenario='ssp585'):
    def relhum(T, Tdp):
        # relative humidity as percent on [0, 100]
        # Used only if variable of interest is hurs
        # https://doi.org/10.1175/1520-0450(1996)035<0601:IMFAOS>2.0.CO;2
        T = T.astype('float64')
        Tdp = Tdp.astype('float64')
        numerator = np.exp(17.625 * Tdp / (243.04 + Tdp))
        denominator = np.exp(17.625 * T / (243.04 + T))
        return 100 * numerator / denominator

    def get_eradata(varname, southern_hem=False):
        # Return numpy array in correct units, leapdays removed
        dataset = ee.ImageCollection("ECMWF/ERA5/DAILY")
        gee_geom = ee.Geometry.Point((latlon[1], latlon[0]))
        data_vars = dataset.select(varname).filter(ee.Filter.date(
            '{0}-01-01'.format(start_year), '{0}-01-01'.format(end_year + 1)))
        success = False
        retries = 0
        while not success:
            try:
                d = data_vars.getRegion(
                    gee_geom, DEFAULT_SPATIAL_RESOLUTION, 'epsg:4326').getInfo()
                success = True
            except:
                retries += 1
                if retries >= 10:
                    raise Exception('Too many fetch-ERA5 retries')
        result = [i[4] for i in d[1:]]
        return np.array(result)
    era_dewpoint = get_eradata('dewpoint_2m_temperature')-273.15
    era_maxtemp = get_eradata('maximum_2m_air_temperature')-273.15
    hurs_obs = relhum(era_maxtemp, era_dewpoint)
    return removeLeapDays(hurs_obs, start_year, end_year, yearshift)


def get_var(varname, model, latlon, start_year=HIST_START, end_year=HIST_END, yearshift=False, scenario='ssp585'):
    if varname == 'hurs' and model in HURS_EXCLUDED:
        raise Exception(
            f'Model {model} does not include complete data for hurs')
    if model != 'ERA5' and start_year < 2015 and end_year >= 2015:
        raise Exception("Requesting hist and non-hist variables in one query")

    if varname == 'hurs' and model == 'ERA5':
        return hurs_era(latlon, start_year, end_year, yearshift)

    if model == 'ERA5':
        dataset = ee.ImageCollection("ECMWF/ERA5/DAILY")
    else:
        dataset = ee.ImageCollection('NASA/GDDP-CMIP6').filter(ee.Filter.eq('model', model)).filter(
            ee.Filter.eq('scenario', [scenario, 'historical'][int(end_year < 2015)]))
    gee_geom = ee.Geometry.Point((latlon[1], latlon[0]))
    if not yearshift:
        success = False
        retries = 0
        while not success:
            try:
                if not yearshift:
                    data_vars = dataset.select([varname, NexGddpCmip6Variables[varname].value['era_varname']][int(model == 'ERA5')]).filter(
                        ee.Filter.date('{0}-01-01'.format(start_year), '{0}-01-01'.format(end_year + 1)))
                else:
                    data_vars = dataset.select([varname, NexGddpCmip6Variables[varname].value['era_varname']][int(model == 'ERA5')]).filter(
                        ee.Filter.date('{0}-07-01'.format(start_year-1), '{0}-07-01'.format(end_year)))
                success = True
            except:
                retries += 1
                if retries >= 10:
                    raise Exception('Too many fetch-ERA5 retries')
        result = [i[4] for i in data_vars.getRegion(
            gee_geom, DEFAULT_SPATIAL_RESOLUTION, 'epsg:4326').getInfo()[1:]]
        result = removeLeapDays(
            np.array(result), start_year, end_year, yearshift)
    return NexGddpCmip6Variables[varname].value[['nex_transform', 'era_transform'][int(model == 'ERA5')]](result)


def get_rmsd(d1, d2):
    def seasonal_means(d):
        mam = []  # 60-151
        jja = []  # 152-243
        son = []  # 244-334
        djf = []  # 335-59
        jan1_idx = 365 + [0, 1][int(calendar.isleap(HIST_START))]
        for year in range(HIST_START+1, HIST_END):
            mam.append(d[jan1_idx + 60: jan1_idx + 152])
            jja.append(d[jan1_idx + 152: jan1_idx + 244])
            son.append(d[jan1_idx + 244: jan1_idx + 335])
            if year < HIST_END - 1:
                if False and calendar.isleap(year):
                    yearlength = 366
                else:
                    yearlength = 365
                djf.append(np.concatenate(
                    (d[jan1_idx + 335: jan1_idx + 365], d[jan1_idx + yearlength: jan1_idx + yearlength + 60])))
            else:
                djf.append(np.concatenate(
                    (d[335: 365], d[365 + [0, 1][int(False and calendar.isleap(HIST_START))]: 425])))
            jan1_idx += 365 + [0, 1][int(False and calendar.isleap(year))]
        return np.array([np.mean(mam, axis=1), np.mean(jja, axis=1), np.mean(son, axis=1), np.mean(djf, axis=1)]).flatten()

    c1 = seasonal_means(d1)
    c2 = seasonal_means(d2)
    return np.sqrt(np.mean(np.sum((c1 - c2)**2)))


def quarters(d, start_year, end_year):
    mam = []  # 60-151
    jja = []  # 152-243
    son = []  # 244-334
    djf = []  # 335-59
    jan1_idx = 365  # + [0, 1][int(calendar.isleap(start_year))]
    for year in range(start_year, end_year):
        tmp = np.concatenate(
            (d[jan1_idx - 365: jan1_idx - 365 + 60], d[jan1_idx + 335: jan1_idx + 365]), axis=0)
        djf.append(tmp)
        mam.append(d[jan1_idx + 60: jan1_idx + 152])
        jja.append(d[jan1_idx + 152: jan1_idx + 244])
        son.append(d[jan1_idx + 244: jan1_idx + 335])

        jan1_idx += 365 + [0, 0][int(False and calendar.isleap(year))]
    mam_res = np.vstack(mam)
    jja_res = np.vstack(jja)
    son_res = np.vstack(son)
    djf_res = np.vstack(djf)
    return mam_res, jja_res, son_res, djf_res


def seasonal_means(d):
    q = quarters(d, HIST_START, HIST_END)
    return np.array([np.mean(q[0], axis=1), np.mean(q[1], axis=1), np.mean(q[2], axis=1), np.mean(q[3], axis=1)])


def quarters(d, start_year, end_year, southern_hem=False):
    # Takes multi-year array and returns data reorganized into seasonal quarters
    q2 = []  # 60-151
    q3 = []  # 152-243
    q4 = []  # 244-334
    q1 = []  # 335-59
    if not southern_hem:
        jan1_idx = 365
        for year in range(start_year, end_year):
            tmp = np.concatenate(
                (d[jan1_idx - 365: jan1_idx - 365 + 60], d[jan1_idx + 335: jan1_idx + 365]), axis=0)
            q1.append(tmp)
            q2.append(d[jan1_idx + 60: jan1_idx + 152])
            q3.append(d[jan1_idx + 152: jan1_idx + 244])
            q4.append(d[jan1_idx + 244: jan1_idx + 335])

            jan1_idx += 365 + [0, 0][int(False and calendar.isleap(year))]
        mam_res = np.vstack(q2)
        jja_res = np.vstack(q3)
        son_res = np.vstack(q4)
        djf_res = np.vstack(q1)
    else:
        jul1_idx = 365
        for year in range(start_year, end_year):
            tmp = np.concatenate(
                (d[jul1_idx - 365: jul1_idx - 365 + 60], d[jul1_idx + 335: jul1_idx + 365]), axis=0)
            q3.append(tmp)
            q4.append(d[jul1_idx + 60: jul1_idx + 152])
            q1.append(d[jul1_idx + 152: jul1_idx + 244])
            q2.append(d[jul1_idx + 244: jul1_idx + 335])

            jul1_idx += 365 + [0, 0][int(False and calendar.isleap(year))]
        mam_res = np.vstack(q4)
        jja_res = np.vstack(q1)
        son_res = np.vstack(q2)
        djf_res = np.vstack(q3)
    return mam_res, jja_res, son_res, djf_res


def calibration_function(hist_obs, hist_mod):
    source = np.sort(hist_obs.flatten())
    target = np.sort(hist_mod.flatten())

    if (np.max(source) == 0 and np.min(source) == 0):
        return np.arange(0, target.size) / target.size
    if (np.max(target) == 0 and np.min(target) == 0):
        return np.arange(0, source.size) / source.size
    new_indices = []
    # source[-1] = target[-1]  # when target[i] greater than all source values, return max index
    for target_idx, target_value in enumerate(target):
        if target_idx < len(source):
            source_value = source[target_idx]
            if source_value > target[-1]:
                new_indices.append(target.size - 1)
            else:
                new_indices.append(np.argmax(target >= source_value))
    return np.array(new_indices) / source.size


def calibrate_interval(uncalibrated_data, calibration_fxn):
    N = len(uncalibrated_data)
    unsorted_uncalib = [(i, idx) for idx, i in enumerate(uncalibrated_data)]
    sorted_uncalib = sorted(unsorted_uncalib)
    result = [0] * N
    for j in range(N):
        X_j = j / (N + 1)
        Y_jprime = calibration_fxn[math.floor(X_j * len(calibration_fxn))]
        jprime = math.floor(Y_jprime * (N + 1))
        result[sorted_uncalib[j][1]] = sorted_uncalib[min(
            len(sorted_uncalib)-1, jprime)][0]

    return result


def calibrate(uncalibrated_data, calibration_fxn):
    mam = []
    jja = []
    son = []
    djf = []
    mam_idx = []
    jja_idx = []
    son_idx = []
    djf_idx = []
    for idx, i in enumerate(uncalibrated_data):
        if idx % 365 >= 60 and idx % 365 < 152:
            mam.append(uncalibrated_data[idx])
            mam_idx.append(idx)
        elif idx % 365 >= 152 and idx % 365 < 244:
            jja.append(uncalibrated_data[idx])
            jja_idx.append(idx)
        elif idx % 365 >= 244 and idx % 365 < 335:
            son.append(uncalibrated_data[idx])
            son_idx.append(idx)
        else:
            djf.append(uncalibrated_data[idx])
            djf_idx.append(idx)

    mam_calib = calibrate_interval(np.array(mam), calibration_fxn[0])
    jja_calib = calibrate_interval(np.array(jja), calibration_fxn[1])
    son_calib = calibrate_interval(np.array(son), calibration_fxn[2])
    djf_calib = calibrate_interval(np.array(djf), calibration_fxn[3])

    result = [0] * len(uncalibrated_data)
    for i in range(len(mam_idx)):
        result[mam_idx[i]] = mam_calib[i]
    for i in range(len(jja_idx)):
        result[jja_idx[i]] = jja_calib[i]
    for i in range(len(son_idx)):
        result[son_idx[i]] = son_calib[i]
    for i in range(len(djf_idx)):
        result[djf_idx[i]] = djf_calib[i]

    return np.array(result)


def get_best_models(varname, latlon, hist_start, hist_end, num_bestmodels):
    # Select three best models based on RMSD of quarterly mean of variable
    hist_obs = get_var(varname, 'ERA5', latlon,
                       start_year=hist_start, end_year=hist_end)
    hist_mods = {}
    rmsds = []
    if varname == 'hurs':
        models = [model for model in MODELS if not model in HURS_EXCLUDED]
    elif varname == 'huss':
        models = [model for model in MODELS if not model in HUSS_EXCLUDED]
    else:
        models = MODELS
    for model in models:
        hist_mod = get_var(varname, model, latlon,
                           start_year=hist_start, end_year=hist_end)
        hist_mods[model] = hist_mod
        rmsds.append((get_rmsd(hist_obs, hist_mod), model))
    rmsds.sort()
    best_models = []
    families = []
    idx = 0
    while len(best_models) < num_bestmodels:
        if not MODEL_INFO[rmsds[idx][1]] in families:
            best_models.append(rmsds[idx][1])
            families.append(MODEL_INFO[rmsds[idx][1]])
        idx += 1
    return best_models, {model: hist_mods[model] for model in best_models}, hist_obs


class NexGddpCmip6Variables(Enum):
    # Unit conversions and variable names for NEX-GDDP-CMIP6 and ERA5
    tas = {
        'era_varname': 'mean_2m_air_temperature',
        'nex_transform': lambda x: x - 273.5,
        'era_transform': lambda x: x - 273.5
    }
    tasmax = {
        'era_varname': 'maximum_2m_air_temperature',
        'nex_transform': lambda x: x - 273.5,
        'era_transform': lambda x: x - 273.5
    },
    tasmin = {
        'era_varname': 'minimum_2m_air_temperature',
        'nex_transform': lambda x: x - 273.5,
        'era_transform': lambda x: x - 273.5
    },
    pr = {
        'era_varname': 'total_precipitation',
        'nex_transform': lambda x: x * 86400,
        'era_transform': lambda x: x * 1000
    },
    hurs = {
        'era_varname': None,
        'nex_transform': lambda x: x,
        'era_transform': lambda x: x
    },
    maxwetbulb = {
        'era_varname': None,
        'nex_transform': lambda x: x,
        'era_transform': lambda x: x
    }


class NexGddpCmip6(Layer):
    OUTPUT_FILE_FORMAT = GTIFF_FILE_EXTENSION
    MAJOR_NAMING_ATTS = None
    MINOR_NAMING_ATTS = None

    """
    get_data() returns daily values of variable for given year range FOR CENTROID OF GIVEN GEOM
    If model not specified, returns for five best models based on RMSD vs ERA5 for historical period
    Leap days are removed
    
    varname is 'tas', 'tasmin', 'tasmax', 'pr', 'hurs', 'sfcWind', 'rlds', 'rsds'
    hurs is %; huss is mass fraction, rlds and rsds are W/m2, sfc is m/s
    temps are converted to deg-C; pr converted to mm/day
    """

    def __init__(self, varname='tasmax', start_year=2040, end_year=2049, scenario='ssp245', num_models=3, **kwargs):
        super().__init__(**kwargs)
        self.varname = varname
        self.start_year = start_year
        self.end_year = end_year
        self.scenario = scenario
        self.num_models = num_models

    def get_data(self, bbox: GeoExtent, spatial_resolution: int = DEFAULT_SPATIAL_RESOLUTION,
                 resampling_method=None):
        spatial_resolution = DEFAULT_SPATIAL_RESOLUTION if spatial_resolution is None else spatial_resolution
        latlon = (bbox.as_geographic_bbox().centroid.y,
                  bbox.as_geographic_bbox().centroid.x)
        best_models, hist_mods, hist_obs = get_best_models(
            'tasmax', latlon, HIST_START, HIST_END, self.num_models)

        calibration_fxns = {}
        for model in best_models:
            o_quarters = quarters(hist_obs, HIST_START, HIST_END)
            m_quarters = quarters(hist_mods[model], HIST_START, HIST_END)
            calibration_fxns[model] = [calibration_function(
                o_quarters[i].flatten(), m_quarters[i].flatten()) for i in range(4)]

        fut_mods = {}
        for model in best_models:
            uncalibrated_data = get_var(
                self.varname, model, latlon, self.start_year, self.end_year)
            fut_mods[model] = calibrate(
                uncalibrated_data, calibration_fxns[model])

        return fut_mods
