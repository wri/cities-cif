# Metrics Reference

All metric classes live in `city_metrix.metrics` and subclass `Metric` (see [Core Concepts](../../getting-started/core-concepts.md)). Each computes one named indicator over an AOI, by composing one or more [layers](../layers/index.md).

Most classes follow a `Name__Unit` naming convention — the suffix tells you the unit of the returned value (e.g. `MeanTreeCover__Percent`, `GhgEmissions__Tonnes`). A small number of preprocessing-style classes (`Era5MetPreprocessingUmep`, `Era5MetPreprocessingUPenn`) don't follow this convention because they return multi-column, mixed-unit DataFrames rather than a single scalar value.

See [All Metrics](metrics.md) for the full table and API reference.

## Import paths

```python
from city_metrix.metrics import MeanTreeCover__Percent, GhgEmissions__Tonnes
```
