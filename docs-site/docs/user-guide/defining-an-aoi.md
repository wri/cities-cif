# Defining an Area of Interest (AOI)

Every layer and metric call needs to know "where". CityMetrix accepts two kinds of input for this, both ultimately wrapped in a `GeoZone` (for `.groupby()` / `Metric.get_metric()`) or `GeoExtent` (for `Layer.get_data()`).

## 1. A polygon (`GeoDataFrame`)

Use this when you already have a boundary file — your own shapefile/GeoJSON, a sub-city district breakdown, or any arbitrary custom polygon.

```python
import geopandas as gpd

city_gdf = gpd.read_file("my_area.geojson")
TreeCover().groupby(city_gdf).mean()
```

You can also pass a raw bounding box tuple `(min_x, min_y, max_x, max_y)` directly to `GeoExtent` when calling `get_data()` instead of `groupby()`:

```python
from city_metrix.metrix_model import GeoExtent
bbox = GeoExtent(bbox=(106.78, -6.23, 106.84, -6.17))
```

Polygon AOIs are **not cached** to S3 — every call recomputes from source.

## 2. A city ID (`city_id` + `aoi_id`)

Use this to reference a boundary already registered with WRI's Cities Data API, as a JSON string:

```python
from city_metrix.metrix_model import GeoZone

geo_zone = GeoZone('{"city_id": "BRA-Florianopolis", "aoi_id": "city_admin_level"}')
```

`aoi_id` must be one of:

| `aoi_id` | Meaning |
|---|---|
| `city_centroid` | A single point at the city's centroid (used for point-based layers, e.g. climate variables that don't need full-polygon zonal stats). |
| `urban_extent` | The city's urban extent boundary, as defined by WRI. |
| `city_admin_level` | The city's official administrative boundary (possibly with sub-city admin units, if the data source defines them). |

Look up valid `city_id` values via the [Cities Indicators API](https://dev.cities-data-api.wri.org/docs).

City AOIs **are cached** to S3 automatically — see [Caching](caching.md).

## Sub-city statistics

If your `GeoDataFrame`/boundary file includes multiple zones (e.g. districts within a city) with a `geo_level` column, `.groupby()` computes zonal statistics per zone automatically — no special API needed.
