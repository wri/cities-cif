# All Metrics

| Class | Unit | Layers used | Description |
|---|---|---|---|
| `AirPollutantAnnualDailyMean__Tonnes` | Tonnes | `Cams`, `CamsSpecies` | Annual mean daily concentration of a selected air pollutant species. |
| `AirPollutantAnnualDailyMax__Tonnes` | Tonnes | `Cams`, `CamsSpecies` | Annual maximum daily concentration of a selected air pollutant species. |
| `AirPollutantAnnualTotalSocialCost__USD` | USD | `Cams`, `CamsSpecies` | Estimated total annual social/health cost of air pollutant emissions. |
| `AirPollutantWhoExceedance__Days` | Days | `Cams`, `CamsSpecies` | Days per year a selected pollutant exceeds its WHO guideline threshold. |
| `AreaFractionalVegetationExceedsThreshold__Percent` | Percent | `FractionalVegetationPercent` | % of area where fractional vegetation meets/exceeds a threshold. |
| `BuiltAreaWithoutTreeCover__Percent` | Percent | `TreeCanopyHeight`, `EsaWorldCover` | % of built-up land with no tree cover above a canopy height threshold. |
| `BuiltLandWithHighLST__Percent` | Percent | `HighLandSurfaceTemperature`, `EsaWorldCover` | % of built-up land experiencing high land surface temperature. |
| `BuiltLandWithLowSurfaceReflectivity__Percent` | Percent | `Albedo`, `EsaWorldCover` | % of built-up land with low surface albedo. |
| `BuiltLandWithVegetation__Percent` | Percent | `EsaWorldCover`, `FractionalVegetationPercent` | % of built-up land with NDVI-based vegetation cover above a threshold. |
| `CanopyAreaPerResident__SquareMeters` | Square Meters | `TreeCanopyHeight`, `WorldPop`, `UrbanLandUse` | Tree canopy area available per resident. |
| `CanopyAreaPerResidentChildren__SquareMeters` | Square Meters | (same, `WorldPopClass.CHILDREN`) | Canopy area per child resident. |
| `CanopyAreaPerResidentElderly__SquareMeters` | Square Meters | (same, `WorldPopClass.ELDERLY`) | Canopy area per elderly resident. |
| `CanopyAreaPerResidentFemale__SquareMeters` | Square Meters | (same, `WorldPopClass.FEMALE`) | Canopy area per female resident. |
| `CanopyAreaPerResidentInformal__SquareMeters` | Square Meters | (same + informal-settlement mask) | Canopy area per resident within informal settlements. |
| `CanopyCoveredPopulation__Percent` | Percent | `WorldPop`, `UrbanLandUse`, `TreeCanopyCoverMask` | % of population living in areas meeting a canopy-coverage threshold. |
| `CanopyCoveredPopulationChildren__Percent` | Percent | (same, `CHILDREN`) | % of children in canopy-covered areas. |
| `CanopyCoveredPopulationElderly__Percent` | Percent | (same, `ELDERLY`) | % of elderly in canopy-covered areas. |
| `CanopyCoveredPopulationFemale__Percent` | Percent | (same, `FEMALE`) | % of females in canopy-covered areas. |
| `CanopyCoveredPopulationInformal__Percent` | Percent | (same + informal-settlement mask) | % of informal-settlement population in canopy-covered areas. |
| `GhgEmissions__Tonnes` | Tonnes | `CamsGhg` | Mean GHG emissions over a zone (optionally CO2e by species/sector). |
| `HabitatConnectivityCoherence__Percent` | Percent | `NaturalAreas` | Degree to which natural-area patches form one connected cluster. |
| `HabitatConnectivityEffectiveMeshSize__Hectares` | Hectares | `NaturalAreas` | Effective mesh size — a habitat fragmentation measure. |
| `HabitatTypesRestored__CoverTypes` | Cover types | `LandCoverSimplifiedGlad`, `LandCoverHabitatChangeGlad` | Count of distinct land-cover types in areas restored to natural habitat. |
| `HospitalsPerTenThousandResidents__Hospitals` | Hospitals (rate) | `OpenStreetMap` (`HOSPITAL`), `WorldPop` | Hospitals per 10,000 residents. |
| `ImperviousArea__Percent` | Percent | `ImperviousSurface` | % of zone land area classified impervious. |
| `ImperviousSurfaceOnUrbanizedLand__Percent` | Percent | `UrbanExtents`, `ImperviousSurface`, `WorldPop` | % of urbanized land covered by impervious surface. |
| `KeyBiodiversityAreaProtected__Percent` | Percent | `WorldPop`, `KeyBiodiversityAreas`, `ProtectedAreas` | % of Key Biodiversity Area under formal legal protection. |
| `KeyBiodiversityAreaUndeveloped__Percent` | Percent | `WorldPop`, `KeyBiodiversityAreas`, `EsaWorldCover` (`BUILT_UP`) | % of Key Biodiversity Area that remains undeveloped. |
| `LandNearNaturalDrainage__Percent` | Percent | `HeightAboveNearestDrainage` | % of land near natural drainage channels. |
| `MeanPM2P5Exposure__MicrogramsPerCubicMeter` | µg/m³ | `AcagPM2p5`, `UrbanLandUse` (optional) | Mean ambient PM2.5 concentration across a zone. |
| `MeanPM2P5ExposurePopWeighted__MicrogramsPerCubicMeter` | µg/m³ | `PopWeightedPM2p5`, `UrbanLandUse` | Population-weighted mean PM2.5 exposure. |
| `MeanPM2P5ExposurePopWeightedChildren__MicrogramsPerCubicMeter` | µg/m³ | (same, children) | Population-weighted PM2.5 exposure for children. |
| `MeanPM2P5ExposurePopWeightedElderly__MicrogramsPerCubicMeter` | µg/m³ | (same, elderly) | Population-weighted PM2.5 exposure for elderly. |
| `MeanPM2P5ExposurePopWeightedFemale__MicrogramsPerCubicMeter` | µg/m³ | (same, female) | Population-weighted PM2.5 exposure for females. |
| `MeanPM2P5ExposurePopWeightedInformal__MicrogramsPerCubicMeter` | µg/m³ | (same + informal-settlement mask) | Population-weighted PM2.5 exposure for informal settlements. |
| `MeanTreeCover__Percent` | Percent | `TreeCover` | Mean % tree cover across a zone. |
| `NaturalAreas__Percent` | Percent | `NaturalAreas` (layer) | % of zone classified as natural land. |
| `BirdRichness__Species` | Species | `SpeciesRichness` (`BIRDS`) | Count of distinct bird species in a zone. |
| `ArthropodRichness__Species` | Species | `SpeciesRichness` (`ARTHROPODS`) | Count of distinct arthropod species in a zone. |
| `VascularPlantRichness__Species` | Species | `SpeciesRichness` (`VASCULAR_PLANTS`) | Count of distinct vascular plant species in a zone. |
| `BirdRichnessInBuiltUpArea__Species` | Species | `SpeciesRichness` (`BIRDS`), `EsaWorldCover` (`BUILT_UP`) | Count of distinct bird species within built-up areas. |
| `ProtectedArea__Percent` | Percent | `ProtectedAreas`, `EsaWorldCover` | % of zone land that is designated/protected area. |
| `RecreationalSpacePerThousand__HectaresPerThousandPersons` | Hectares / 1,000 persons | `WorldPop`, `OpenStreetMap` (`OPEN_SPACE`) | Recreational/open space per 1,000 residents. |
| `RiparianLandWithVegetationOrWater__Percent` | Percent | `RiparianAreas`, `NdwiSentinel2`, `FractionalVegetationPercent` | % of riparian land covered by water or vegetation. |
| `RiverineOrCoastalFloodRiskArea__Percent` | Percent | `AqueductFlood` (riverine + coastal) | % of zone exposed to riverine/coastal flood risk. |
| `SteeplySlopedLandWithVegetation__Percent` | Percent | `Slope`, `FractionalVegetationPercent` | % of steeply sloped land that is also vegetated. |
| `TreeCarbonFlux__Tonnes` | Tonnes | `CarbonFluxFromTrees` | Net carbon flux from trees in a zone. |
| `UrbanOpenSpace__Percent` | Percent | `EsaWorldCover` (`BUILT_UP`), `OpenStreetMap` (`OPEN_SPACE`) | % of built-up urban land that is open/recreational space. |
| `VegetationWaterChangeGainArea__SquareMeters` | Square Meters | `VegetationWaterMap` (gain) | Area gained in vegetation/water cover between two dates. |
| `VegetationWaterChangeLossArea__SquareMeters` | Square Meters | `VegetationWaterMap` (loss) | Area lost in vegetation/water cover between two dates. |
| `VegetationWaterChangeGainLoss__Ratio` | Ratio | `VegetationWaterMap` (gain + loss + baseline) | Net gain-minus-loss ratio of vegetation/water change, normalized by start area. |
| `WaterCover__Percent` | Percent | `SurfaceWater`, `NdwiSentinel2` | % of zone area covered by surface water. |

!!! note "Non-conforming preprocessing classes"
    `Era5MetPreprocessingUmep` and `Era5MetPreprocessingUPenn` don't follow the `Name__Unit` convention — they produce multi-column, mixed-unit DataFrames of meteorological forcing data (built on `Era5HottestDay`) for use by external microclimate models (UMEP, UPenn), rather than a single scalar indicator.

## API

::: city_metrix.metrics.air_pollutant_annual_daily_statistic.AirPollutantAnnualDailyMean__Tonnes
::: city_metrix.metrics.air_pollutant_annual_daily_statistic.AirPollutantAnnualDailyMax__Tonnes
::: city_metrix.metrics.air_pollutant_annual_daily_statistic.AirPollutantAnnualTotalSocialCost__USD
::: city_metrix.metrics.air_pollutant_who_exceedance_days.AirPollutantWhoExceedance__Days
::: city_metrix.metrics.area_fracveg_exceeds_threshold.AreaFractionalVegetationExceedsThreshold__Percent
::: city_metrix.metrics.built_area_without_tree_cover.BuiltAreaWithoutTreeCover__Percent
::: city_metrix.metrics.built_land_with_high_land_surface_temperature.BuiltLandWithHighLST__Percent
::: city_metrix.metrics.built_land_with_low_surface_reflectivity.BuiltLandWithLowSurfaceReflectivity__Percent
::: city_metrix.metrics.built_land_with_vegetation.BuiltLandWithVegetation__Percent
::: city_metrix.metrics.canopy_area_per_resident.CanopyAreaPerResident__SquareMeters
::: city_metrix.metrics.canopy_area_per_resident.CanopyAreaPerResidentChildren__SquareMeters
::: city_metrix.metrics.canopy_area_per_resident.CanopyAreaPerResidentElderly__SquareMeters
::: city_metrix.metrics.canopy_area_per_resident.CanopyAreaPerResidentFemale__SquareMeters
::: city_metrix.metrics.canopy_area_per_resident.CanopyAreaPerResidentInformal__SquareMeters
::: city_metrix.metrics.canopy_covered_population.CanopyCoveredPopulation__Percent
::: city_metrix.metrics.canopy_covered_population.CanopyCoveredPopulationChildren__Percent
::: city_metrix.metrics.canopy_covered_population.CanopyCoveredPopulationElderly__Percent
::: city_metrix.metrics.canopy_covered_population.CanopyCoveredPopulationFemale__Percent
::: city_metrix.metrics.canopy_covered_population.CanopyCoveredPopulationInformal__Percent
::: city_metrix.metrics.era5_met_preprocessing_umep_gee.Era5MetPreprocessingUmep
::: city_metrix.metrics.era5_met_preprocessing_upenn_gee.Era5MetPreprocessingUPenn
::: city_metrix.metrics.future_climate_hazard.FutureHeatwaveFrequency__Heatwaves
::: city_metrix.metrics.future_climate_hazard.FutureHeatwaveMaxDuration__Days
::: city_metrix.metrics.future_climate_hazard.FutureDaysAbove35__Days
::: city_metrix.metrics.future_climate_hazard.FutureAnnualMaxTemp__DegreesCelsius
::: city_metrix.metrics.future_climate_hazard.FutureExtremePrecipitationDays__Days
::: city_metrix.metrics.ghg_emissions.GhgEmissions__Tonnes
::: city_metrix.metrics.habitat_connectivity.HabitatConnectivityCoherence__Percent
::: city_metrix.metrics.habitat_connectivity.HabitatConnectivityEffectiveMeshSize__Hectares
::: city_metrix.metrics.habitat_types_restored.HabitatTypesRestored__CoverTypes
::: city_metrix.metrics.hospitals_per_ten_thousand_residents.HospitalsPerTenThousandResidents__Hospitals
::: city_metrix.metrics.impervious_area.ImperviousArea__Percent
::: city_metrix.metrics.impervious_surface_on_urbanized_land.ImperviousSurfaceOnUrbanizedLand__Percent
::: city_metrix.metrics.key_biodiversity_area.KeyBiodiversityAreaProtected__Percent
::: city_metrix.metrics.key_biodiversity_area.KeyBiodiversityAreaUndeveloped__Percent
::: city_metrix.metrics.land_near_natural_drainage.LandNearNaturalDrainage__Percent
::: city_metrix.metrics.mean_pm2p5_exposure.MeanPM2P5Exposure__MicrogramsPerCubicMeter
::: city_metrix.metrics.mean_pm2p5_exposure.MeanPM2P5ExposurePopWeighted__MicrogramsPerCubicMeter
::: city_metrix.metrics.mean_pm2p5_exposure.MeanPM2P5ExposurePopWeightedChildren__MicrogramsPerCubicMeter
::: city_metrix.metrics.mean_pm2p5_exposure.MeanPM2P5ExposurePopWeightedElderly__MicrogramsPerCubicMeter
::: city_metrix.metrics.mean_pm2p5_exposure.MeanPM2P5ExposurePopWeightedFemale__MicrogramsPerCubicMeter
::: city_metrix.metrics.mean_pm2p5_exposure.MeanPM2P5ExposurePopWeightedInformal__MicrogramsPerCubicMeter
::: city_metrix.metrics.mean_tree_cover.MeanTreeCover__Percent
::: city_metrix.metrics.natural_areas.NaturalAreas__Percent
::: city_metrix.metrics.number_species.BirdRichness__Species
::: city_metrix.metrics.number_species.ArthropodRichness__Species
::: city_metrix.metrics.number_species.VascularPlantRichness__Species
::: city_metrix.metrics.number_species.BirdRichnessInBuiltUpArea__Species
::: city_metrix.metrics.protected_area.ProtectedArea__Percent
::: city_metrix.metrics.recreational_space_per_thousand.RecreationalSpacePerThousand__HectaresPerThousandPersons
::: city_metrix.metrics.riparian_land_with_vegetation_or_water.RiparianLandWithVegetationOrWater__Percent
::: city_metrix.metrics.riverine_or_coastal_flood_risk_area.RiverineOrCoastalFloodRiskArea__Percent
::: city_metrix.metrics.steeply_sloped_land_with_vegetation.SteeplySlopedLandWithVegetation__Percent
::: city_metrix.metrics.tree_carbon_flux.TreeCarbonFlux__Tonnes
::: city_metrix.metrics.urban_open_space.UrbanOpenSpace__Percent
::: city_metrix.metrics.vegetation_water_change.VegetationWaterChangeGainArea__SquareMeters
::: city_metrix.metrics.vegetation_water_change.VegetationWaterChangeLossArea__SquareMeters
::: city_metrix.metrics.vegetation_water_change.VegetationWaterChangeGainLoss__Ratio
::: city_metrix.metrics.water_cover.WaterCover__Percent
