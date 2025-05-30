# Release Notes

## 2025/05/30
1. Added write/read for metrics in CSV format, instead of geojson.
2. Adjusted temp-file handling for both windows and Linux.
3. Improved caching logic.

## 2025/05/24
1. CDB-322. Fixed error in UTGlobus-to-Overture conflation that had produced many-to-one matches and resulting errors in height computation.
2. Modified computation of UTGlobus heights to use mode or median computation. See updated https://gfw.atlassian.net/wiki/spaces/CIT/pages/1971912734/Primary+Raster+Layers+for+Thermal+Comfort+Modeling

## 2025/05/12
1. Moved OpenUrban layer from C-TCM to CIF. Former location: https://github.com/wri/cities-thermal-comfort-modeling/blob/main/src/workers/open_urban.py

## 2025/05/09
1. Re-implemented OvertureBuildingsDSM to fix a bug and improve cross-tile correspondence in building elevation.

## 2025/04/30
1. Updated NasaDEM and AlosDSM to emit smoother surface interpolations for non-default resolutions.

## 2025/04/25
1. Renamed overture_buildings_w_height_raster to overture_buildings_dsm and updated to return raster of Overture buildings combined with DEM.
1. Added ut_globus_city_handler package for storing geopackage and query function for UT Globus cities.
   2. This is a temporary solution until we have time to develop a service for finding Globus city by geometry.
   

## 2025/04/21
1. Combined all bases classes into one file
1. Removed retrieve_cached_city_data function call from derived classes
1. Removed allow_cache_retrieval argument from get_data() method in layers 
1. Removed CifCacheSettings
1. Updated zonal statistics to handle large, tiled retrievals
1. Updated zonal statistics to handle multi-level city and admin polygons
1. Added test_write_all_metrics_by_city.py to write metrics by city
1. Converted some functions to static class methods to improve performance
1. Changed AWS profile for credentials file to "cities-data-dev"
1. TODOs:
   1. Performance of large cities needs to be tested since only small and moderate size have been run so far
   2. Update the naming conventions wiki: https://gfw.atlassian.net/wiki/spaces/CIT/pages/1886126084/Proposal+for+layer-id+naming

## 2025/04/14
1. Added timeout_decorator to environment.yml
2. Warning: Some tests in tests/resources folder write intermediate results to a shared S3 bucket, so there is some potential for collision between concurrent runs.
3. Simplified tests and renamed some tests
4. Refocused layer-write tests on query by city name instead of by bbox.

## 2025/04/9
1. Merged some Layers and Metrics functions
2. Increased granularity for controling whether individual tests are run by converting the old EXECUTE_IGNORED_TESTS boolean values into enums.

## 2025/04/7
1. Created a Metric base class with get_data() and two write functions
2. Converted each existing Metric function into a Metric class with get_data() function
3. Added tests to write output of each class to a local system file
4. Modified skip-if decorator for write tests to use DumpRunLevel enum

## 2025/04/2
1. Added download of cached CIF results from S3 or a local directory when available.
   1. Caching is enabled by running the set_cache_settings function prior to getting or writing data.
2. Added standardized naming of cached file storage such as into S3 buckets.
   1. The current naming convention must be reviewed by users. This wiki discusses naming conventions https://gfw.atlassian.net/wiki/spaces/CIT/pages/1886126084/Proposal+for+layer-id+naming
3. Added the layer_dao.py file for handling calls to the cities-data-api API and S3.
4. Added requirements for AWS credentials file.

## 2025/03/18
1. Added ability to specify city_id+aoi for GeoExtent.
2. Bounding coordinates for city_id+aoi are currently read from the cities-data-api.wri.org url since it is stable. Longer term, this url must be replace by the dev.cities-data-api.wri.org url once that API has stabilized.

## 2025/02/10 V0.2.1
1. Added GeoExtent class supporting bbox coordinates in both UTM and geographic coordinates.
   1. redefined the bbox parameter on get_data() function as GeoExtent class.
   2. included several functions on GeoExtent to support conversion from/to projections and other functionality.
2. Moved spatial_resolution and resampling_method from Layer class definitions to get_data() functions in all Layers.
3. Extensive re-write of fishnet function to output in both UTM and geographic space.

