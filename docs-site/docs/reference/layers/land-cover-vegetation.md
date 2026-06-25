# Land Cover & Vegetation

| Class | Key params | Returns | Data source | Description |
|---|---|---|---|---|
| `EsaWorldCover` | `land_cover_class=None`, `year=2020` | raster | ESA WorldCover (GEE `ESA/WorldCover/v100`/`v200`) | Global 10m land cover classification, optionally filtered to one class via `EsaWorldCoverClass`. |
| `LandCoverGlad` | `year=2020` | raster | GEE `projects/glad/GLCLU2020` | Raw GLAD global land cover/land use classification for a given year. |
| `LandCoverSimplifiedGlad` | `year=2020` | raster | derived from `LandCoverGlad` | Reclassifies raw GLAD codes into a simplified 0–10 class scheme. |
| `LandCoverHabitatGlad` | `year=2020` | raster | derived from `LandCoverSimplifiedGlad` | Binary habitat mask (natural classes 1–6 = habitat). |
| `LandCoverHabitatChangeGlad` | `start_year=2000`, `end_year=2020` | raster | derived from `LandCoverHabitatGlad` (two years) | Habitat-change code: gained vs. lost habitat between two years. |
| `NaturalAreas` | `year=2020` | raster | derived from `EsaWorldCover` | Binary "natural area" mask reclassified from ESA WorldCover. |
| `TreeCover` | `min_tree_cover=None`, `max_tree_cover=None` | raster | GEE `projects/wri-datalab/TropicalTreeCover` + `TTC-nontropics` | Merged global tropical/non-tropical percent tree cover. |
| `TreeCanopyHeight` | `height=None`, `index_aggregation=False`, `worldpop_version=1` | raster | GEE Meta `CanopyHeight` | Global tree canopy height (meters), optionally aligned to WorldPop grid. |
| `TreeCanopyHeightCTCM` | `height=None` | raster | same Meta canopy-height collection | CTCM-workflow variant of canopy height (buffered then trimmed to AOI). |
| `TreeCanopyCoverMask` | `height=None`, `percentage=30` | raster | derived from `TreeCanopyHeight` | Binary tree-canopy-cover mask thresholded by % cover. |
| `NdviSentinel2` | `year=2021`, `min_threshold=None` | raster | GEE `COPERNICUS/S2_HARMONIZED` | NDVI computed from Sentinel-2, optionally binarized at a threshold. |
| `FractionalVegetationPercent` | `min_threshold=None`, `year=2025`, `index_aggregation=False`, `worldpop_version=1` | raster | GEE Dynamic World + S2 SR + Cloud Score+ | Percent vegetation fraction via NDVI endmember unmixing. |
| `VegetationWaterMap` | `start_date`, `end_date`, `greenwater_layer` | raster | Sentinel-2 (cloud-masked) | Annual NDVI/NDWI trend composites; gain/loss vegetation-water change masks. |
| `OpenUrban` | `band='b1'` | raster | GEE `projects/wri-datalab/cities/OpenUrban` | High-resolution urban land-use/land-cover classification (buildings, roads, parking, green space) via `OpenUrbanClass`. |

## API

::: city_metrix.layers.esa_world_cover.EsaWorldCover
::: city_metrix.layers.esa_world_cover.EsaWorldCoverClass
::: city_metrix.layers.glad_lulc.LandCoverGlad
::: city_metrix.layers.glad_lulc.LandCoverSimplifiedGlad
::: city_metrix.layers.glad_lulc.LandCoverHabitatGlad
::: city_metrix.layers.glad_lulc.LandCoverHabitatChangeGlad
::: city_metrix.layers.natural_areas.NaturalAreas
::: city_metrix.layers.tree_cover.TreeCover
::: city_metrix.layers.tree_canopy_height.TreeCanopyHeight
::: city_metrix.layers.tree_canopy_height_for_ctcm.TreeCanopyHeightCTCM
::: city_metrix.layers.tree_canopy_cover_mask.TreeCanopyCoverMask
::: city_metrix.layers.ndvi_sentinel2_gee.NdviSentinel2
::: city_metrix.layers.fractional_vegetation_percent.FractionalVegetationPercent
::: city_metrix.layers.vegetation_water_map.VegetationWaterMap
::: city_metrix.layers.open_urban.OpenUrban
::: city_metrix.layers.open_urban.OpenUrbanClass
