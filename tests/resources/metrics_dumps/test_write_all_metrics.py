# This code is mostly intended for manual execution
# Execution configuration is specified in the conftest file
import pytest

from city_metrix.metrics import *
from tests.conftest import create_fishnet_gdf_for_testing
from tests.resources.bbox_constants import BBOX_IDN_JAKARTA, BBOX_IDN_JAKARTA_LARGE
from tests.resources.conftest import DUMP_RUN_LEVEL, DumpRunLevel
from tests.resources.tools import prep_output_path, verify_file_is_populated

SAMPLE_TILED_SINGLE_ZONE = (
    GeoZone(create_fishnet_gdf_for_testing(BBOX_IDN_JAKARTA.coords, 0.1).reset_index()))

SAMPLE_TILED_ZONES = (
    GeoZone(create_fishnet_gdf_for_testing(BBOX_IDN_JAKARTA.coords, 0.05).reset_index()))

SAMPLE_TILED_LARGE_ZONES = (
    GeoZone(create_fishnet_gdf_for_testing(BBOX_IDN_JAKARTA_LARGE.coords, 0.5).reset_index()))

# TODO - groupby fails for small zones that return null values from AcagPM2p5 layer. How should system handle such nulls


@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_built_land_with_high_land_surface_temperature(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','built_land_with_high_land_surface_temperature.csv')

    BuiltLandWithHighLST().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_built_land_with_low_surface_reflectivity(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','built_land_with_low_surface_reflectivity.csv')

    BuiltLandWithLowSurfaceReflectivity().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_canopy_area_per_resident_children(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','canopy_area_per_resident_children.csv')

    CanopyAreaPerResidentChildren().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_canopy_area_per_resident_elderly(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','canopy_area_per_resident_elderly.csv')

    CanopyAreaPerResidentElderly().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_canopy_area_per_resident_female(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','canopy_area_per_resident_female.csv')

    CanopyAreaPerResidentFemale().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_canopy_area_per_resident_informal(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','canopy_area_per_resident_informal.csv')

    CanopyAreaPerResidentInformal().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_era_5_met_preprocessing(target_folder):
    zones = SAMPLE_TILED_SINGLE_ZONE
    file_path = prep_output_path(target_folder, 'metric','era_5_met_preprocessing.csv')

    Era5MetPreprocessing().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    file_path = prep_output_path(target_folder, 'metric','mean_pm2p5_exposure.csv')

    MeanPM2P5Exposure().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure_pop_weighted_children(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    file_path = prep_output_path(target_folder, 'metric','mean_pm2p5_exposure_pop_weighted_children.csv')

    MeanPM2P5ExposurePopWeightedChildren().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure_pop_weighted_elderly(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    file_path = prep_output_path(target_folder, 'metric','mean_pm2p5_exposure_pop_weighted_elderly.csv')

    MeanPM2P5ExposurePopWeightedElderly().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure_pop_weighted_female(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    file_path = prep_output_path(target_folder, 'metric','mean_pm2p5_exposure_pop_weighted_female.csv')

    MeanPM2P5ExposurePopWeightedFemale().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure_pop_weighted_informal(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    file_path = prep_output_path(target_folder, 'metric','mean_pm2p5_exposure_pop_weighted_informal.csv')

    MeanPM2P5ExposurePopWeightedInformal().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_tree_cover(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','mean_tree_cover.csv')

    MeanTreeCover().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_natural_areas(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','natural_areas.csv')

    NaturalAreasPercent().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_PercentAreaFracvegExceedsThreshold(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','percent_area_fracveg_exceeds_threshold.csv')

    PercentAreaFracvegExceedsThreshold().write(zones, file_path)
    assert verify_file_is_populated(file_path)

# TODO Test fails for Teresina since data are not available. Find a different city for it to succeed.
# @pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
# def test_write_PercentBuiltAreaWithoutTreeCover(target_folder):
#     zones = SAMPLE_TILED_ZONES
#     file_path = prep_output_path(target_folder, 'metric', 'percent_build_area_without_tree_cover.csv')
#
#     PercentBuiltAreaWithoutTreeCover().write(zones, file_path)
#     assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_percent_area_impervious(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','percent_area_impervious.csv')

    PercentAreaImpervious().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_PercentCanopyCoveredPopulation(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','percent_canopy_covered_population.csv')

    PercentCanopyCoveredPopulation().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_percent_protected_area(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','percent_protected_area.csv')

    PercentProtectedArea().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_recreational_space_per_capita(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','recreational_space_per_capita.csv')

    RecreationalSpacePerCapita().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_urban_open_space(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','urban_open_space.csv')

    UrbanOpenSpace().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_vegetation_water_change_gain_area(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','vegetation_water_change_gain_area.csv')

    VegetationWaterChangeGainArea().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_vegetation_water_change_loss_area(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','vegetation_water_change_loss_area.csv')

    VegetationWaterChangeLossArea().write(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_vegetation_water_change_gain_loss_ratio(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','vegetation_water_change_gain_loss_ratio.csv')

    VegetationWaterChangeGainLossRatio().write(zones, file_path)
    assert verify_file_is_populated(file_path)

