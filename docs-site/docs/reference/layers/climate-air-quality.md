# Climate & Air Quality

| Class | Key params | Returns | Data source | Description |
|---|---|---|---|---|
| `AcagPM2p5` | `year=2023`, `return_above=0` | raster | GEE `projects/wri-datalab/cities/aq/acag_annual_pm2p5_{year}` | Annual mean PM2.5 concentration surface. |
| `Albedo` | `start_date`, `end_date`, `threshold=None` | raster | GEE S2 SR + Cloud Probability | Mean surface albedo from cloud-masked Sentinel-2. |
| `AlbedoCloudMasked` | `start_date`, `end_date`, `index_aggregation=False`, `zonal_stats='median'`, `num_seasons=3`, `worldpop_version=1` | raster | GEE S2 SR + Cloud Score+ | Multi-season median/mean albedo, optionally aligned to WorldPop grid. |
| `Cams` | `start_date`, `end_date`, `species=None` | raster | CDS API `cams-global-reanalysis-eac4` | Atmospheric pollutant concentrations (NO2, SO2, O3, PM2.5, PM10, CO) via `CamsSpecies`. |
| `CamsGhg` | `species=None`, `sector='sum'`, `co2e=True`, `year=2024` | raster | GEE `projects/wri-datalab/cams-glob-ant` | Annual GHG emissions (CO2/CH4/N2O or CO2e) by sector. |
| `CarbonFluxFromTrees` | (none) | raster | GEE GFW net-flux-forest-extent (Harris et al. 2021) | Average annual net carbon flux from forest, 2001–2023. |
| `Era5HottestDay` (`era5_hottest_day.py`) | `start_date=None`, `end_date=None`, `seasonal_utc_offset=0.0` | raster | GEE ERA5_LAND/HOURLY + CDS API | Finds the hottest day in range, pulls full hourly ERA5 variables via CDS. |
| `Era5HottestDay` (`era5_hottest_day_gee.py`) | `start_date=None`, `end_date=None`, `seasonal_utc_offset=0.0` | raster | GEE ERA5_LAND/DAILY_AGGR, HOURLY, ERA5/HOURLY | Pure-GEE variant of the above, avoiding the CDS dependency. |
| `LandSurfaceTemperature` | `start_date`, `end_date`, `hot_season_length=None`, `use_modis=False` | raster | GEE Landsat 8 C02/T1_L2 thermal or MODIS MOD11A2 | Percentile/median composite of land surface temperature. |
| `HighLandSurfaceTemperature` | `start_date`, `end_date`, `index_aggregation=False`, `high_lst=False`, `use_modis=False`, `worldpop_version=1` | raster | derived from `LandSurfaceTemperature` + `WorldPop` | Hot-spot LST pixels more than 3°C above the local mean. |
| `NexGddpCmip6` | `varname='tasmax'`, `start_year=2040`, `end_year=2049`, `scenario='ssp245'`, `num_models=3` | dict of arrays | GEE `NASA/GDDP-CMIP6` + ERA5/DAILY (calibration) | Bias-corrected future climate projections from best-fit CMIP6 models, via `NexGddpCmip6Variables`. |
| `PopWeightedPM2p5` | `worldpop_agesex_classes=[]`, `worldpop_year=2020`, `worldpop_version=1`, `acag_year=2023`, `acag_return_above=0` | raster | composes `WorldPop` + `AcagPM2p5` | PM2.5 concentration weighted by relative population density. |

!!! note "Duplicate class name"
    Both `Era5HottestDay` classes share a name but live in different modules (`era5_hottest_day` vs. `era5_hottest_day_gee`) — import from the specific submodule if ambiguity matters.

## API

::: city_metrix.layers.acag_pm2p5.AcagPM2p5
::: city_metrix.layers.albedo.Albedo
::: city_metrix.layers.albedo_cloud_masked.AlbedoCloudMasked
::: city_metrix.layers.cams.Cams
::: city_metrix.layers.cams.CamsSpecies
::: city_metrix.layers.cams_ghg.CamsGhg
::: city_metrix.layers.carbon_flux_from_trees.CarbonFluxFromTrees
::: city_metrix.layers.era5_hottest_day.Era5HottestDay
::: city_metrix.layers.era5_hottest_day_gee.Era5HottestDay
::: city_metrix.layers.land_surface_temperature.LandSurfaceTemperature
::: city_metrix.layers.high_land_surface_temperature.HighLandSurfaceTemperature
::: city_metrix.layers.nex_gddp_cmip6.NexGddpCmip6
::: city_metrix.layers.nex_gddp_cmip6.NexGddpCmip6Variables
::: city_metrix.layers.pop_weighted_pm2p5.PopWeightedPM2p5
