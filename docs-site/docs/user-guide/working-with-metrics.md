# Working with Metrics

A **metric** is any class in `city_metrix.metrics`. Each one is a pre-built indicator that composes one or more [layers](working-with-layers.md) into a single named calculation, so you don't have to assemble the `.mask().groupby()` chain yourself.

## Naming convention

Metric classes are named `Name__Unit`, where the suffix after the double underscore tells you the unit of the returned value:

```python
from city_metrix.metrics import MeanTreeCover__Percent, GhgEmissions__Tonnes, MeanPM2P5Exposure__MicrogramsPerCubicMeter
```

A handful of preprocessing-style classes (e.g. `Era5MetPreprocessingUmep`, `Era5MetPreprocessingUPenn`) don't follow this convention because they return multi-column, mixed-unit DataFrames rather than a single scalar indicator — see the [Metrics reference](../reference/metrics/metrics.md) for those.

## Computing a metric

```python
from city_metrix.metrics import MeanTreeCover__Percent

result = MeanTreeCover__Percent().get_metric(geo_zone=city_gdf)
```

`get_metric(geo_zone, spatial_resolution=None)` returns a `pandas.Series` (one value) or `pandas.DataFrame` (one row per zone, for multi-zone AOIs).

Some metrics take their own constructor parameters, e.g. a year or pollutant species:

```python
from city_metrix.metrics import GhgEmissions__Tonnes
from city_metrix.layers import CamsSpecies

GhgEmissions__Tonnes(species=CamsSpecies.CO2, year=2023).get_metric(city_gdf)
```

## Writing results

```python
MeanTreeCover__Percent().write(city_gdf, target_file_path="mean_tree_cover.csv")
MeanTreeCover__Percent().write_as_geojson(city_gdf, target_file_path="mean_tree_cover.geojson")
```

## Caching

Like layers, metric results for **city AOIs** are cached to S3 automatically (`.retrieve_metric()` reads cache-first). Polygon AOIs are not cached. See [Caching](caching.md).

## Finding the right metric

Browse the full [Metrics reference](../reference/metrics/metrics.md) for the complete list with units and underlying layers, or look at which layer(s) a metric uses if you want to compute something similar with custom parameters instead of the default.
