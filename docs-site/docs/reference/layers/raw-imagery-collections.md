# Raw Imagery Collections

These layers give direct access to raw multi-band satellite imagery, for cases where the higher-level derived layers (NDVI, land cover, etc.) don't cover what you need.

| Class | Key params | Returns | Data source | Description |
|---|---|---|---|---|
| `LandsatCollection2` | `bands` (required), `start_date=2013-01-01`, `end_date=2023-01-01` | raster | AWS STAC `landsat-c2-l2` | Raw multi-band Landsat Collection 2 Level 2 surface data, QA-masked. |
| `Sentinel2Level2` | `bands` (required), `start_date=2013-01-01`, `end_date=2023-01-01` | raster | AWS STAC `sentinel-2-l2a` | Cloud-masked Sentinel-2 L2A bands at 10m, SCL-masked. |

## API

::: city_metrix.layers.landsat_collection_2.LandsatCollection2
::: city_metrix.layers.sentinel_2_level_2.Sentinel2Level2
