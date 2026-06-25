# CityMetrix

**CityMetrix** (`city_metrix`) is a Python package from WRI's Cities Indicators Framework (CIF) for extracting geospatial data **layers** and computing urban sustainability **metrics** for any city or custom area of interest, using global open datasets.

It answers two related questions for any urban geography you care about:

1. **What does the data look like here?** — pull a raw or processed geospatial layer (land cover, tree canopy, elevation, air quality, building footprints, flood risk, ...) clipped to your area.
2. **How does this area score?** — compute a pre-defined indicator (e.g. *mean tree cover*, *% impervious surface*, *PM2.5 exposure*) as zonal statistics over your area.

## Two ways to define "where"

Every layer and metric takes an **area of interest (AOI)** as input, in one of two forms:

- **A polygon** — any `GeoDataFrame` or bounding box you already have.
- **A city ID** — a WRI city identifier plus an AOI type (`city_centroid`, `urban_extent`, or `city_admin_level`), resolved automatically against the Cities Data API.

See [Defining an AOI](user-guide/defining-an-aoi.md) for details.

## A 30-second example

```python
from city_metrix.layers import TreeCover, EsaWorldCover, EsaWorldCoverClass
from city_metrix.metrics import MeanTreeCover__Percent

# 1. Define an AOI as a polygon (any GeoDataFrame works)
import geopandas as gpd
city_gdf = gpd.read_file("jakarta.geojson")

# 2. Pull a layer, masked to built-up land, and aggregate it yourself
tree_in_builtup = (
    TreeCover(min_tree_cover=10)
    .mask(EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP))
    .groupby(city_gdf)
    .count()
)

# 3. ...or just use a pre-built metric
mean_cover = MeanTreeCover__Percent().get_metric(city_gdf)
```

## Where to go next

- New to the package? Start with [Installation](getting-started/installation.md) and the [Quickstart](getting-started/quickstart.md).
- Want to understand the moving parts? Read [Core Concepts](getting-started/core-concepts.md).
- Looking for a specific dataset or indicator? Jump straight to the [Layers reference](reference/layers/index.md) or [Metrics reference](reference/metrics/index.md).
