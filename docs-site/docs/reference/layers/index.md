# Layers Reference

All layer classes live in `city_metrix.layers` and subclass `Layer` (see [Core Concepts](../../getting-started/core-concepts.md)). Each one returns either a **raster** (`xarray.DataArray`) or **vector** (`GeoDataFrame`) clipped to your AOI.

Layers are grouped below by theme. Each category page has an overview table (parameters, data source, output type) followed by full auto-generated signatures for every class.

| Category | Layers |
|---|---|
| [Land Cover & Vegetation](land-cover-vegetation.md) | Land cover classification, tree cover/canopy, vegetation indices |
| [Elevation & Terrain](elevation-terrain.md) | Digital elevation/surface models, slope |
| [Hydrology & Flood Risk](hydrology-flood-risk.md) | Surface water, drainage, riparian zones, flood inundation |
| [Climate & Air Quality](climate-air-quality.md) | Air pollutants, GHG emissions, albedo, land surface temperature, future climate projections |
| [Buildings & Urban Form](buildings-urban-form.md) | Building footprints/heights, urban extents, land use, OpenStreetMap features |
| [Biodiversity & Protected Areas](biodiversity-protected-areas.md) | Key biodiversity areas, protected areas, species richness |
| [Population & Socioeconomic](population-socioeconomic.md) | Gridded population |
| [Raw Imagery Collections](raw-imagery-collections.md) | Raw Landsat / Sentinel-2 band access |

!!! note "Duplicate class name"
    Two distinct classes are both named `Era5HottestDay`, in different files: `city_metrix.layers.era5_hottest_day` (uses the CDS API for full hourly variables) and `city_metrix.layers.era5_hottest_day_gee` (a pure-GEE variant of the same concept, avoiding the CDS dependency). Import from the specific submodule if you need to disambiguate.

## Import paths

All classes are re-exported from `city_metrix.layers`, so in most cases you can simply do:

```python
from city_metrix.layers import TreeCover, EsaWorldCover, EsaWorldCoverClass
```
