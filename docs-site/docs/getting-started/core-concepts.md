# Core Concepts

CityMetrix is built around four classes, all defined in `city_metrix.metrix_model`.

## `GeoZone` and `GeoExtent` — the AOI

These two classes represent "where" you want data, and normalize the two input styles described in [Defining an AOI](../user-guide/defining-an-aoi.md):

- A geometry (`GeoDataFrame`, bbox tuple, or `GeoZone`/`GeoExtent`) — `geo_type = GEOMETRY`.
- A `city_id` + `aoi_id` JSON string — `geo_type` is `CITY_AREA` or `CITY_CENTROID`, and the actual boundary is resolved from the Cities Data API.

Both classes normalize the AOI to a consistent bounding box, centroid, and CRS, and provide `as_utm_bbox()` / `as_geographic_bbox()` to convert between projections — most raster processing happens in UTM (meters), since Earth Engine and zonal-statistics math need a projected CRS.

You'll mostly interact with `GeoZone` (when calling `.groupby(...)` or `Metric.get_metric(...)`) and `GeoExtent` (when calling `Layer.get_data(...)`).

## `Layer` — one geospatial dataset

Every class in `city_metrix.layers` subclasses `Layer` and implements:

```python
def get_data(self, bbox: GeoExtent, spatial_resolution: int = None, resampling_method: str = None):
    ...
```

`get_data()` returns either an `xarray.DataArray` (raster) or a `GeoDataFrame` (vector), clipped to `bbox`. Beyond `get_data()`, `Layer` provides:

- **`.mask(*layers)`** — returns a new `Layer` that excludes pixels/features not covered by the given mask layer(s).
- **`.groupby(geo_zone)`** — returns a `LayerGroupBy`, which computes zonal statistics (`.mean()`, `.count()`, `.sum()`) over one or more zones, automatically tiling large AOIs into a fishnet grid behind the scenes so Earth Engine requests stay within memory limits.
- **`.write(bbox, target_file_path)`** — writes the layer's data to a local or S3 GeoTIFF/GeoJSON.
- **`.retrieve_data(bbox, ...)`** — same as `get_data()`, but reads from the S3 cache first if a cached result already exists for this layer + AOI + parameters.

## `Metric` — one computed indicator

Every class in `city_metrix.metrics` subclasses `Metric` and implements:

```python
def get_metric(self, geo_zone: GeoZone, spatial_resolution: int = None):
    ...
```

`get_metric()` composes one or more `Layer` objects (usually via `.mask()` and `.groupby()`) and returns a `pandas.Series` or `pandas.DataFrame` of computed values — one per zone in `geo_zone`. `Metric` mirrors `Layer`'s caching/writing API: `.write()`, `.write_as_geojson()`, `.retrieve_metric()`.

## Caching

Both `Layer` and `Metric` results for **city AOIs** are automatically cached to S3, keyed by class name and non-default constructor parameters (see [Caching](../user-guide/caching.md)). Custom polygon AOIs are not cached. This is why every layer/metric class declares `OUTPUT_FILE_FORMAT`, `MAJOR_NAMING_ATTS`, and `MINOR_NAMING_ATTS` class attributes — they control the cache key.

## Putting it together

```text
GeoZone / GeoExtent  →  "where"
        +
Layer (chained via .mask())  →  "what raw/derived data"
        +
.groupby(...).mean()/.count()/.sum()  →  "zonal statistics"
        =
Metric.get_metric()  →  the same pattern, pre-packaged as a named indicator
```
