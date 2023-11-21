from .layer import Layer


class DailyEra5Aggregate(Layer):
    def __init__(self, variable, start_year=2013, end_year=2022, **kwargs):
        super().__init__(**kwargs)
        self.start_year = start_year
        self.end_year = end_year


def fix_accum_var_dims(ds, var):
    # Some varibles like precip have extra time bounds varibles, we drop them here to allow merging with other variables

    # Select variable of interest (drops dims that are not linked to current variable)
    ds = ds[[var]]

    if var in ['air_temperature_at_2_metres',
               'dew_point_temperature_at_2_metres',
               'air_pressure_at_mean_sea_level',
               'northward_wind_at_10_metres',
               'eastward_wind_at_10_metres']:

        ds = ds.rename({'time0': 'valid_time_end_utc'})

    elif var in ['precipitation_amount_1hour_Accumulation',
                 'integral_wrt_time_of_surface_direct_downwelling_shortwave_flux_in_air_1hour_Accumulation']:

        ds = ds.rename({'time1': 'valid_time_end_utc'})

    else:
        print("Warning, Haven't seen {var} varible yet! Time renaming might not work.".format(var=var))

    return ds


def s3open(path):
    fs = s3fs.S3FileSystem(anon=True, default_fill_cache=False,
                           config_kwargs={'max_pool_connections': 20})
    return s3fs.S3Map(path, s3=fs)


def open_era5_range(start_year, end_year, variables):
    ''' Opens ERA5 monthly Zarr files in S3, given a start and end year (all months loaded) and a list of variables'''
    file_pattern = 'era5-pds/zarr/{year}/{month}/data/{var}.zarr/'

    years = list(np.arange(start_year, end_year + 1, 1))
    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

    l = []
    for var in variables:
        print(var)

        # Get files
        files_mapper = [s3open(file_pattern.format(year=year, month=month, var=var)) for year in years for month in
                        months]

        # Look up correct time dimension by variable name
        if var in ['precipitation_amount_1hour_Accumulation']:
            concat_dim = 'time1'
        else:
            concat_dim = 'time0'

        # Lazy load
        ds = xr.open_mfdataset(files_mapper, engine='zarr',
                               concat_dim=concat_dim, combine='nested',
                               coords='minimal', compat='override', parallel=True)

        # Fix dimension names
        ds = fix_accum_var_dims(ds, var)
        l.append(ds)

    ds_out = xr.merge(l)

    return ds_out