# Caching

CityMetrix caches computed layer and metric results to S3 so repeated requests for the same data don't re-hit Earth Engine, AWS, or other sources every time.

## When caching applies

Caching only kicks in for **city AOIs** (`aoi_id` of `city_centroid`, `urban_extent`, or `city_admin_level`) — not for arbitrary polygon/`GeoDataFrame` AOIs, which are always recomputed from source.

| Call | Cache behavior |
|---|---|
| `layer.get_data(bbox)` | Never cached — always computes. |
| `layer.retrieve_data(bbox)` | Cache-first for city AOIs; computes and opportunistically caches on a miss. |
| `layer.cache_city_data(bbox, s3_bucket, s3_env)` | Explicitly populates the cache, skipping if already cached (unless `force_data_refresh=True`). |
| `metric.get_metric(geo_zone)` | Never cached — always computes. |
| `metric.retrieve_metric(geo_zone)` | Cache-first for city AOIs. |
| `metric.cache_city_metric(geo_zone, s3_bucket, s3_env)` | Explicitly populates the cache. |

## Cache keys

Each layer/metric class declares three class attributes that determine its cache key (see `city_metrix/cache_manager.py`):

- `OUTPUT_FILE_FORMAT` — file extension used in storage (`tif`, `geojson`, `csv`, ...).
- `MAJOR_NAMING_ATTS` — constructor parameters that materially change the output and must be reflected in the cache path.
- `MINOR_NAMING_ATTS` — parameters that are recorded but don't need a distinct cache entry per value.

Layer cache paths follow:

```
data/{env}/{layer_name}/{file_format}/{city_id}__{admin_level}__{layer_id}
```

where `env` is `published` (production) or `pre-release` (development).

## Environments

Pass `s3_env="published"` (default/production) or `s3_env="pre-release"` (development) to target a different cache namespace — useful when testing changes to a layer without overwriting the production cache.

## Practical implications

- If you're iterating on a *custom* polygon, you won't pay (or benefit from) any caching — every run recomputes.
- If you're computing metrics for a known WRI `city_id` that's already been processed, `retrieve_data`/`retrieve_metric` calls will be fast (cache hits) until you change a parameter that's in `MAJOR_NAMING_ATTS`.
- Use `force_data_refresh=True` on `cache_city_data`/`cache_city_metric` to bypass a stale cache deliberately.
