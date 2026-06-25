# Working with Layers

A **layer** is any class in `city_metrix.layers`. Every layer subclasses `Layer` and represents one geospatial dataset, raw or derived.

## Constructing a layer

Most layers take optional parameters in their constructor that affect *what* gets extracted (a year, a class filter, a date range) — not *where*:

```python
from city_metrix.layers import TreeCover, EsaWorldCover, EsaWorldCoverClass

TreeCover(min_tree_cover=10, max_tree_cover=80)
EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP, year=2021)
```

Check the [Layers reference](../reference/layers/index.md) for each class's parameters.

## Getting raw data

```python
from city_metrix.metrix_model import GeoExtent

bbox = GeoExtent(bbox=(106.78, -6.23, 106.84, -6.17))
data = TreeCover().get_data(bbox, spatial_resolution=10)
```

This returns:

- an **`xarray.DataArray`** for raster layers (most land cover, elevation, climate, and imagery layers), or
- a **`GeoDataFrame`** for vector layers (buildings, OSM features, protected areas, species records).

Common `get_data()` parameters:

| Parameter | Meaning |
|---|---|
| `bbox` | A `GeoExtent` describing the area to extract. |
| `spatial_resolution` | Raster resolution in meters; defaults vary per layer. |
| `resampling_method` | `"bilinear"`, `"bicubic"`, or `"nearest"` — interpolation used when resampling continuous rasters. |

## Masking

`.mask(*layers)` filters one layer down to only the pixels/features also covered by other layer(s) — e.g. tree cover *within* built-up land:

```python
masked = TreeCover().mask(EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP))
```

Masks compose: you can chain `.mask()` calls or pass multiple layers at once.

## Zonal statistics

`.groupby(geo_zone)` returns a `LayerGroupBy` you can aggregate:

```python
masked.groupby(city_gdf).mean()    # average value per zone
masked.groupby(city_gdf).count()   # pixel/feature count per zone
masked.groupby(city_gdf).sum()     # summed value per zone
```

Large AOIs are automatically split into a fishnet tile grid behind the scenes so requests stay within Earth Engine's memory limits — you don't need to do anything differently for a small district vs. a megacity.

## Writing and caching

```python
TreeCover().write(bbox, target_file_path="tree_cover.tif")           # write to a local/S3 path, no caching
TreeCover().retrieve_data(bbox)                                       # read from S3 cache if available, else compute + cache
```

See [Caching](caching.md) for when caching applies.
