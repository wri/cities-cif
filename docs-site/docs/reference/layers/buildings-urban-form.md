# Buildings & Urban Form

| Class | Key params | Returns | Data source | Description |
|---|---|---|---|---|
| `AverageNetBuildingHeight` | (none) | raster | GEE `projects/wri-datalab/GHSL/GHS-BUILT-H-ANBH_GLOBE_R2023A` | Average building height per cell (GHSL). |
| `BuiltUpHeight` | (none) | raster | GEE `JRC/GHSL/P2023A/GHS_BUILT_H/2018` | Built-up structure height, 2018. |
| `GlobalBuildingAtlas` | (none) | vector | GEE asset tiles (sat-io Global Building Atlas) | Building footprint polygons with height estimates. |
| `OpenBuildings` | `country='USA'` | vector | GEE `projects/sat-io/open-datasets/VIDA_COMBINED/{country}` | Open building footprints for a country (VIDA). |
| `OvertureBuildings` | (none) | vector | Overture Maps (downloaded via CLI) | Building footprint polygons from Overture Maps. |
| `OvertureBuildingsHeight` | `city=""` | vector | composes `OvertureBuildings`, `GlobalBuildingAtlas`, `UtGlobus`, `AverageNetBuildingHeight` | Best-estimate building height per Overture footprint, with a provenance column. |
| `OvertureBuildingsDSM` | `city=""` | raster | composes `OvertureBuildingsHeight` + `FabDEM` | Digital surface model from rasterized buildings plus bare-earth DEM. |
| `UtGlobus` | `city=""` | vector | GEE `projects/sat-io/open-datasets/UT-GLOBUS/{city}` | Building footprints with height/volume/surface-area attributes. |
| `ImperviousSurface` | `year=2018` | raster | GEE `Tsinghua/FROM-GLC/GAIA/v10` | Binary impervious/built-surface mask as of a given year. |
| `UrbanExtents` | `year=2020`, `buffer=None` | vector | GEE `projects/wri-datalab/cities/urban_land_use/.../urbanextents_unions_{year}` | WRI's official urban extent boundary polygon(s) for a city/year. |
| `UrbanLandUse` | `band='lulc'`, `ulu_class=None` | raster | GEE `projects/wri-datalab/cities/urban_land_use/V1` | WRI urban land-use classification (open space, informal/formal housing, etc.). |
| `OpenStreetMap` | `osm_class=OpenStreetMapClass.ALL`, `worldpop_version=1` | vector | OpenStreetMap (via `osmnx`) | OSM features (buildings, roads, parks, etc.) filtered by category. |
| `OpenStreetMapAmenityCount` | `osm_class=OpenStreetMapClass.ALL`, `worldpop_version=1` | raster | `OpenStreetMap` rasterized onto the WorldPop grid | Gridded count of OSM amenity features per cell. |

## API

::: city_metrix.layers.average_net_building_height.AverageNetBuildingHeight
::: city_metrix.layers.built_up_height.BuiltUpHeight
::: city_metrix.layers.global_building_atlas.GlobalBuildingAtlas
::: city_metrix.layers.open_buildings.OpenBuildings
::: city_metrix.layers.overture_buildings.OvertureBuildings
::: city_metrix.layers.overture_buildings_w_height.OvertureBuildingsHeight
::: city_metrix.layers.overture_buildings_dsm.OvertureBuildingsDSM
::: city_metrix.layers.ut_globus.UtGlobus
::: city_metrix.layers.impervious_surface.ImperviousSurface
::: city_metrix.layers.urban_extents.UrbanExtents
::: city_metrix.layers.urban_land_use.UrbanLandUse
::: city_metrix.layers.open_street_map.OpenStreetMapClass
::: city_metrix.layers.open_street_map.OpenStreetMap
::: city_metrix.layers.open_street_map.OpenStreetMapAmenityCount
