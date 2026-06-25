# Biodiversity & Protected Areas

| Class | Key params | Returns | Data source | Description |
|---|---|---|---|---|
| `KeyBiodiversityAreas` | `country_code_iso3=None`, `worldpop_version=1` | raster | S3 WRI cities-indicators KBA GeoJSONs, rasterized | Binary mask of pixels inside a Key Biodiversity Area. |
| `ProtectedAreas` | `status=[...]`, `status_year=2024`, `iucn_cat=[...]` | vector | GEE `WCMC/WDPA/current/polygons` | Officially protected area polygons (WDPA), filtered by status/IUCN category. |
| `SpeciesRichness` | `taxon=GBIFTaxonClass.BIRDS`, `start_year=2019`, `end_year=2024`, `mask_layer=None` | vector (1-row) | GBIF occurrence API (research-grade) | Estimated species richness via species-accumulation curve extrapolation. |

## API

::: city_metrix.layers.key_biodiversity_areas.KeyBiodiversityAreas
::: city_metrix.layers.protected_areas.ProtectedAreas
::: city_metrix.layers.species_richness.GBIFTaxonClass
::: city_metrix.layers.species_richness.SpeciesRichness
