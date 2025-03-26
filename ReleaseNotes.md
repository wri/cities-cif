# Release Notes

## 2025/03/18
1. Added ability to specify city_id+aoi for GeoExtent.
2. Bounding coordinates for city_id+aoi are currently read from the cities-data-api.wri.org url since it is stable. Longer term, this url must be replace by the dev.cities-data-api.wri.org url once that API has stabilized.

## 2025/02/10 V0.2.1
1. Added GeoExtent class supporting bbox coordinates in both UTM and geographic coordinates.
   1. redefined the bbox parameter on get_data() function as GeoExtent class.
   2. included several functions on GeoExtent to support conversion from/to projections and other functionality.
2. Moved spatial_resolution and resampling_method from Layer class definitions to get_data() functions in all Layers.
3. Extensive re-write of fishnet function to output in both UTM and geographic space.

