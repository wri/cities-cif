# Release Notes

## 2025/02/10 V0.2.1
1. Added GeoExtent class supporting bbox coordinates in both UTM and geographic coordinates.
   1. redefined the bbox parameter on get_data() function as GeoExtent class.
   2. included several functions on GeoExtent to support conversion from/to projections and other functionality.
2. Moved spatial_resolution and resampling_method from Layer class definitions to get_data() functions in all Layers.
3. Extensive re-write of fishnet function to output in both UTM and geographic space.

