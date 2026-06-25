# Elevation & Terrain

| Class | Key params | Returns | Data source | Description |
|---|---|---|---|---|
| `AlosDSM` | (none) | raster | GEE `JAXA/ALOS/AW3D30/V3_2` | Digital surface model elevation (terrain + objects). |
| `NasaDEM` | (none) | raster | GEE `NASA/NASADEM_HGT/001` | Ground elevation (SRTM-derived), Gaussian-smoothed. |
| `FabDEM` | (none) | raster | GEE `projects/sat-io/open-datasets/FABDEM` | Bare-earth DEM with forests/buildings removed. |
| `Slope` | `min_threshold=None` | raster | derived from `NasaDEM` via `ee.Terrain.slope` | Terrain slope in degrees, optionally binarized at a threshold. |
| `HighSlope` | `slope_threshold=10` | raster | derived from `NasaDEM` via `xrspatial.slope` | Mask of terrain exceeding a slope threshold. |

## API

::: city_metrix.layers.alos_dsm.AlosDSM
::: city_metrix.layers.nasa_dem.NasaDEM
::: city_metrix.layers.fab_dem.FabDEM
::: city_metrix.layers.slope.Slope
::: city_metrix.layers.high_slope.HighSlope
