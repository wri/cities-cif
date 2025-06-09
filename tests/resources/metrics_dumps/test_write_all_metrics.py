# This code is mostly intended for manual execution
# Execution configuration is specified in the conftest file
import pytest

from city_metrix.constants import DEFAULT_STAGING_ENV
from city_metrix.metrics import *
from tests.conftest import create_fishnet_gdf_for_testing
from tests.resources.bbox_constants import BBOX_IDN_JAKARTA, BBOX_IDN_JAKARTA_LARGE
from tests.resources.conftest import DUMP_RUN_LEVEL, DumpRunLevel
from tests.resources.tools import prep_output_path, verify_file_is_populated, cleanup_cache_files

SAMPLE_TILED_SINGLE_ZONE = (
    GeoZone(create_fishnet_gdf_for_testing(BBOX_IDN_JAKARTA.coords, 0.1).reset_index()))

SAMPLE_TILED_ZONES = (
    GeoZone(create_fishnet_gdf_for_testing(BBOX_IDN_JAKARTA.coords, 0.05).reset_index()))

SAMPLE_TILED_LARGE_ZONES = (
    GeoZone(create_fishnet_gdf_for_testing(BBOX_IDN_JAKARTA_LARGE.coords, 0.5).reset_index()))

# TODO - groupby fails for small zones that return null values from AcagPM2p5 layer. How should system handle such nulls

PRESERVE_RESULTS_ON_OS = False # False - Default for check-in


@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_built_land_with_high_land_surface_temperature(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','built_land_with_high_land_surface_temperature.csv')

    metric_obj = BuiltLandWithHighLST()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_built_land_with_low_surface_reflectivity(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','built_land_with_low_surface_reflectivity.csv')

    metric_obj = BuiltLandWithLowSurfaceReflectivity()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_canopy_area_per_resident_children(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','canopy_area_per_resident_children.csv')

    metric_obj = CanopyAreaPerResidentChildren()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_canopy_area_per_resident_elderly(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','canopy_area_per_resident_elderly.csv')

    metric_obj = CanopyAreaPerResidentElderly()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_canopy_area_per_resident_female(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','canopy_area_per_resident_female.csv')

    metric_obj = CanopyAreaPerResidentFemale()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_canopy_area_per_resident_informal(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','canopy_area_per_resident_informal.csv')

    metric_obj = CanopyAreaPerResidentInformal()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_era_5_met_preprocessing(target_folder):
    zones = SAMPLE_TILED_SINGLE_ZONE
    file_path = prep_output_path(target_folder, 'metric','era_5_met_preprocessing.csv')

    metric_obj = Era5MetPreprocessing()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    file_path = prep_output_path(target_folder, 'metric','mean_pm2p5_exposure.csv')

    metric_obj = MeanPM2P5Exposure()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure_pop_weighted_children(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    file_path = prep_output_path(target_folder, 'metric','mean_pm2p5_exposure_pop_weighted_children.csv')

    metric_obj = MeanPM2P5ExposurePopWeightedChildren()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure_pop_weighted_elderly(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    file_path = prep_output_path(target_folder, 'metric','mean_pm2p5_exposure_pop_weighted_elderly.csv')

    metric_obj = MeanPM2P5ExposurePopWeightedElderly()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure_pop_weighted_female(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    file_path = prep_output_path(target_folder, 'metric','mean_pm2p5_exposure_pop_weighted_female.csv')

    metric_obj = MeanPM2P5ExposurePopWeightedFemale()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_pm2p5_exposure_pop_weighted_informal(target_folder):
    zones = SAMPLE_TILED_LARGE_ZONES
    file_path = prep_output_path(target_folder, 'metric','mean_pm2p5_exposure_pop_weighted_informal.csv')

    metric_obj = MeanPM2P5ExposurePopWeightedInformal()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_mean_tree_cover(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','mean_tree_cover.csv')

    metric_obj = MeanTreeCover()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_natural_areas(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','natural_areas.csv')

    metric_obj = NaturalAreasPercent()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_PercentAreaFracvegExceedsThreshold(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','percent_area_fracveg_exceeds_threshold.csv')

    metric_obj = PercentAreaFracvegExceedsThreshold()
    _write_verify(metric_obj, zones, file_path)

# TODO Test fails for Teresina since data are not available. Find a different city for it to succeed.
# @pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
# def test_write_PercentBuiltAreaWithoutTreeCover(target_folder):
#     zones = SAMPLE_TILED_ZONES
#     file_path = prep_output_path(target_folder, 'metric', 'percent_build_area_without_tree_cover.csv')
#
#     metric_obj = PercentBuiltAreaWithoutTreeCover()
#     _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_percent_area_impervious(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','percent_area_impervious.csv')

    metric_obj = PercentAreaImpervious()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_PercentCanopyCoveredPopulation(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','percent_canopy_covered_population.csv')

    metric_obj = PercentCanopyCoveredPopulation()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_percent_protected_area(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','percent_protected_area.csv')

    metric_obj = PercentProtectedArea()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_recreational_space_per_capita(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','recreational_space_per_capita.csv')

    metric_obj = RecreationalSpacePerCapita()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_urban_open_space(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','urban_open_space.csv')

    metric_obj = UrbanOpenSpace()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_vegetation_water_change_gain_area(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','vegetation_water_change_gain_area.csv')

    metric_obj = VegetationWaterChangeGainArea()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_vegetation_water_change_loss_area(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','vegetation_water_change_loss_area.csv')

    metric_obj = VegetationWaterChangeLossArea()
    _write_verify(metric_obj, zones, file_path)

@pytest.mark.skipif(DUMP_RUN_LEVEL != DumpRunLevel.RUN_FAST_ONLY, reason=f"Skipping since DUMP_RUN_LEVEL set to {DUMP_RUN_LEVEL}")
def test_write_vegetation_water_change_gain_loss_ratio(target_folder):
    zones = SAMPLE_TILED_ZONES
    file_path = prep_output_path(target_folder, 'metric','vegetation_water_change_gain_loss_ratio.csv')

    metric_obj = VegetationWaterChangeGainLossRatio()
    _write_verify(metric_obj, zones, file_path)


def _write_verify(metric_obj, zones, file_path):
    metric_obj.write(geo_zone=zones, s3_env=DEFAULT_STAGING_ENV, output_uri=file_path)
    assert verify_file_is_populated(file_path)
    if not PRESERVE_RESULTS_ON_OS:
        cleanup_cache_files(None, None, None, file_path)