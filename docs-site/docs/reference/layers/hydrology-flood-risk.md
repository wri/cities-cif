# Hydrology & Flood Risk

| Class | Key params | Returns | Data source | Description |
|---|---|---|---|---|
| `SurfaceWater` | `year=2021` | raster | derived from `NdwiSentinel2` | Surface water mask via histogram minimum-threshold split of NDWI. |
| `NdwiSentinel2` | `year=2021`, `min_threshold=None` | raster | GEE `COPERNICUS/S2_HARMONIZED` | NDWI from Sentinel-2, optionally binarized to a water mask. |
| `HeightAboveNearestDrainage` | `river_head=1000`, `thresh=1`, `nanval=None` | raster | GEE `users/gena/GlobalHAND` + MODIS water mask | Flood-prone/drainage-proximity areas (HAND model). |
| `RiparianAreas` | `river_head=1000`, `thresh=0` | raster | `HeightAboveNearestDrainage` + GEE `JRC/GSW1_4/GlobalSurfaceWater` | Riparian buffer zones around rivers/water bodies. |
| `AqueductFlood` | `return_period_c='rp0100'`, `return_period_r='rp00100'`, `year=2050`, `climate='rcp4p5'`, `subsidence='nosub'`, `sea_level_rise_scenario=50`, `report_threshold=None` | raster | WRI Aqueduct flood inundation collection (GEE) | Combined coastal + riverine flood inundation depth, optionally binarized. |

## API

::: city_metrix.layers.surface_water.SurfaceWater
::: city_metrix.layers.ndwi_sentinel2_gee.NdwiSentinel2
::: city_metrix.layers.height_above_nearest_drainage.HeightAboveNearestDrainage
::: city_metrix.layers.riparian_areas.RiparianAreas
::: city_metrix.layers.aqueduct_flood.AqueductFlood
