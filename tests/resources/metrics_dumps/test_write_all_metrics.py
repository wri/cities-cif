# This code is mostly intended for manual execution
# Execution configuration is specified in the conftest file
import os
import pytest

from city_metrix.metrics import *
from tests.conftest import create_fishnet_gdf_for_testing
from tests.resources.bbox_constants import BBOX_IDN_JAKARTA, BBOX_IDN_JAKARTA_LARGE
from tests.resources.conftest import prep_output_path, verify_file_is_populated, DUMP_RUN_LEVEL, DumpRunLevel
from tests.tools.general_tools import create_target_folder

SAMPLE_TILED_SINGLE_ZONE = (
    create_fishnet_gdf_for_testing(BBOX_IDN_JAKARTA.coords, 0.1).reset_index())

SAMPLE_TILED_ZONES = (
    create_fishnet_gdf_for_testing(BBOX_IDN_JAKARTA.coords, 0.05).reset_index())

SAMPLE_TILED_LARGE_ZONES = (
    create_fishnet_gdf_for_testing(BBOX_IDN_JAKARTA_LARGE.coords, 0.5).reset_index())

# TODO - groupby fails for small zones that return null values from AcagPM2p5 layer. How should system handle such nulls


@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_built_land_with_high_land_surface_temperature(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)

    file_path = prep_output_path(target_metrics_folder, 'built_land_with_high_land_surface_temperature.geojson')
    BuiltLandWithHighLST().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_built_land_with_low_surface_reflectivity(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'built_land_with_low_surface_reflectivity.geojson')

    BuiltLandWithLowSurfaceReflectivity().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_built_land_without_tree_cover(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'built_land_without_tree_cover.geojson')

    BuiltLandWithoutTreeCover().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)


@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_canopy_area_per_resident_children(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'canopy_area_per_resident_children.geojson')

    CanopyAreaPerResidentChildren().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_canopy_area_per_resident_elderly(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'canopy_area_per_resident_elderly.geojson')

    CanopyAreaPerResidentElderly().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_canopy_area_per_resident_female(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'canopy_area_per_resident_female.geojson')

    CanopyAreaPerResidentFemale().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_canopy_area_per_resident_informal(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'canopy_area_per_resident_informal.geojson')

    CanopyAreaPerResidentInformal().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_era_5_met_preprocessing(target_folder):
    zones = SAMPLE_TILED_SINGLE_ZONE
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'era_5_met_preprocessing.geojson')

    Era5MetPreprocessing().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure_pop_weighted_children(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'mean_pm2p5_exposure.geojson')

    MeanPM2P5ExposurePopWeightedChildren().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure_pop_weighted_elderly(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'mean_pm2p5_exposure_pop_weighted_elderly.geojson')

    MeanPM2P5ExposurePopWeightedElderly().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure_pop_weighted_female(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'mean_pm2p5_exposure_pop_weighted_female.geojson')

    MeanPM2P5ExposurePopWeightedFemale().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure_pop_weighted_informal(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'mean_pm2p5_exposure_pop_weighted_informal.geojson')

    MeanPM2P5ExposurePopWeightedInformal().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_tree_cover(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'mean_tree_cover.geojson')

    MeanTreeCover().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_natural_areas(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'natural_areas.geojson')

    NaturalAreasPercent().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_percent_area_impervious(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'percent_area_impervious.geojson')

    PercentAreaImpervious().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)


@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_percent_protected_area(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'percent_protected_area.geojson')

    PercentProtectedArea().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)


@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_recreational_space_per_capita(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'recreational_space_per_capita.geojson')

    RecreationalSpacePerCapita().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)


@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_urban_open_space(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'urban_open_space.geojson')

    UrbanOpenSpace().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)


@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_vegetation_water_change_gain_area(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'vegetation_water_change_gain_area.geojson')

    VegetationWaterChangeGainArea().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_vegetation_water_change_loss_area(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'vegetation_water_change_loss_area.geojson')

    VegetationWaterChangeLossArea().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL == DumpRunLevel.RUN_NONE, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_vegetation_water_change_gain_loss_ratio(target_folder):
    zones = SAMPLE_TILED_ZONES
    target_metrics_folder = str(os.path.join(target_folder, 'metrics'))
    create_target_folder(target_metrics_folder, False)
    file_path = prep_output_path(target_metrics_folder, 'vegetation_water_change_gain_loss_ratio.geojson')

    VegetationWaterChangeGainLossRatio().write_as_geojson(zones, file_path)
    assert verify_file_is_populated(file_path)

