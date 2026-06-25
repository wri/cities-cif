# Quickstart

This walks through both ways of telling CityMetrix *where* you want data, and the two main things you can do once you have an AOI: pull a **layer**, or compute a **metric**.

## Option A: AOI from your own polygon

If you already have a city or district boundary as a `GeoDataFrame`, just use it directly:

```python
import geopandas as gpd
from city_metrix.layers import TreeCover

city_gdf = gpd.read_file("jakarta.geojson")

mean_cover = TreeCover().groupby(city_gdf).mean()
print(mean_cover)
```

## Option B: AOI from a WRI city ID

If you want to use a boundary already known to the Cities Data API, build a `GeoExtent`/`GeoZone` from a `city_id` + `aoi_id` JSON snippet instead:

```python
from city_metrix.metrix_model import GeoZone
from city_metrix.layers import TreeCover

geo_zone = GeoZone('{"city_id": "BRA-Florianopolis", "aoi_id": "city_admin_level"}')

mean_cover = TreeCover().groupby(geo_zone).mean()
```

`aoi_id` can be `city_centroid`, `urban_extent`, or `city_admin_level`. You can look up valid `city_id` values via the [Cities Indicators API](https://dev.cities-data-api.wri.org/docs).

## Pulling a layer's raw data

Every layer implements `get_data()`, which returns a raster (`xarray.DataArray`) or vector (`GeoDataFrame`) clipped to a bounding box:

```python
from city_metrix.metrix_model import GeoExtent
from city_metrix.layers import EsaWorldCover

bbox = GeoExtent(bbox=(106.78, -6.23, 106.84, -6.17))  # min_x, min_y, max_x, max_y
land_cover = EsaWorldCover().get_data(bbox)
```

## Combining layers: masks and zonal stats

Layers can be chained: use one layer as a **mask** over another, then run zonal statistics with `.groupby(...).mean()/.count()/.sum()`:

```python
from city_metrix.layers import TreeCover, EsaWorldCover, EsaWorldCoverClass

result = (
    TreeCover(min_tree_cover=10)
    .mask(EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP))
    .groupby(city_gdf)
    .count()
)
```

## Using a pre-built metric

Most common indicators are already implemented as `Metric` classes in `city_metrix.metrics`, so you don't need to assemble the layer chain yourself:

```python
from city_metrix.metrics import MeanTreeCover__Percent

mean_cover = MeanTreeCover__Percent().get_metric(geo_zone=city_gdf)
```

Metric class names follow a `Name__Unit` convention — see [Working with Metrics](../user-guide/working-with-metrics.md).

## Writing results to a file

```python
TreeCover().write(bbox, target_file_path="tree_cover.tif")
MeanTreeCover__Percent().write(city_gdf, target_file_path="mean_tree_cover.csv")
```

Next: read [Core Concepts](core-concepts.md) to understand what's actually happening under the hood.
