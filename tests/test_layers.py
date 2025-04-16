import math

import pytest
import numpy as np

from city_metrix.layers import *
from city_metrix.layers.layer_tools import get_projection_name
from tests.conftest import EXECUTE_IGNORED_TESTS
from tests.resources.bbox_constants import BBOX_USA_OR_PORTLAND_2
from tests.tools.spatial_tools import get_rounded_gdf_geometry

# Tests are implemented for an area where we have LULC and is a stable region
COUNTRY_CODE_FOR_BBOX = 'USA'
CITY_CODE_FOR_BBOX = 'portland'
BBOX = BBOX_USA_OR_PORTLAND_2
BBOX_AS_UTM = BBOX.as_utm_bbox()


def test_acag_pm2p5():
    data = AcagPM2p5().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 2, 6.57, 6.57, 1, 0)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = AcagPM2p5().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))


def test_albedo():
    data = Albedo().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 3, 0.0262, 0.56, 9797, 0)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = Albedo().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_alos_dsm():
    data = AlosDSM().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 0, 66, 1122, 0)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = AlosDSM().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_aqueduct_flood():
    data = AqueductFlood().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 4.09, 4.09, 21, 79)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = AqueductFlood().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))
    
def test_average_net_building_height():
    data = AverageNetBuildingHeight().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 0, 14.61, 100, 0)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = AverageNetBuildingHeight().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_built_up_height():
    data = BuiltUpHeight().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 0, 14.61, 100, 0)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = BuiltUpHeight().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason="CDS API needs personal access token file to run")
def test_cams():
    data = Cams().get_data(BBOX)
    assert np.size(data) > 0
    # TODO Add value testing
    utm_bbox_data = Cams().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason="CDS API needs personal access token file to run")
def test_era_5_hottest_day():
    data = Era5HottestDay().get_data(BBOX)
    assert np.size(data) > 0
    # TODO Add value testing
    utm_bbox_data = Era5HottestDay().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_esa_world_cover():
    land_cover_class = EsaWorldCoverClass.BUILT_UP
    data = EsaWorldCover(land_cover_class=land_cover_class).get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 50, 50, 3242, 6555)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = EsaWorldCover(land_cover_class=land_cover_class).get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_fractional_vegetation():
    data = FractionalVegetation().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 0.00000006, 1, 9797, 0)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = FractionalVegetation().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_height_above_nearest_drainage():
    data = HeightAboveNearestDrainage().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 1, 1, 9, 1113)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = HeightAboveNearestDrainage().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_high_land_surface_temperature():
    data = HighLandSurfaceTemperature().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 40.47, 42.35, 150, 972)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = HighLandSurfaceTemperature().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_high_slope():
    data = HighSlope().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 10.07, 22.01, 143, 979)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = HighSlope().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_impervious_surface():
    data = ImperviousSurface().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 1.0, 1.0, 100, 0)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = ImperviousSurface().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_land_cover_glad():
    data = LandCoverGlad().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 23.0, 250.0, 1122, 0)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = LandCoverGlad().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_land_cover_habitat_glad():
    data = LandCoverHabitatGlad().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 2, 0.0, 1.0, 1122, 0)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = LandCoverHabitatGlad().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_land_cover_habitat_change():
    data = LandCoverHabitatChangeGlad().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 0.0, 0.0, 1122, 0)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = LandCoverHabitatChangeGlad().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_land_cover_simplified_glad():
    data = LandCoverSimplifiedGlad().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 1.0, 9.0, 1122, 0)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = LandCoverSimplifiedGlad().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_land_surface_temperature():
    data = LandSurfaceTemperature().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 17.54, 30.46, 1122, 0)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = LandSurfaceTemperature().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_landsat_collection_2():
    bands = ["blue"]
    data = LandsatCollection2(bands).get_data(BBOX)
    assert np.size(data.blue) > 0
    # TODO Add value testing

def test_nasa_dem():
    data = NasaDEM().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 3.0, 56.0, 1122, 0)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = NasaDEM().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_natural_areas():
    data = NaturalAreas().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 0.0, 1.0, 9797, 0)
    assert get_projection_name(data.rio.crs.to_epsg()) == 'utm'
    utm_bbox_data = NaturalAreas().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_ndvi_sentinel2():
    data = NdviSentinel2(year=2023).get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 2, 0.087, 0.852, 9797, 0)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = NdviSentinel2(year=2023).get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_openbuildings():
    data = OpenBuildings(COUNTRY_CODE_FOR_BBOX).get_data(BBOX)
    assert np.size(data) > 0
    assert_vector_stats(data, 'area_in_meters', 1, 8.1, 15967.0, 1111, 0)
    assert get_projection_name(data.crs.srs) == 'utm'
    utm_bbox_data = OpenBuildings(COUNTRY_CODE_FOR_BBOX).get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_open_street_map():
    data = OpenStreetMap(osm_class=OpenStreetMapClass.ROAD).get_data(BBOX)
    assert np.size(data) > 0
    assert_vector_stats(data, 'highway', None, 'primary', 'tertiary', 147, 0)
    assert get_projection_name(data.crs.srs) == 'utm'
    utm_bbox_data = OpenStreetMap(osm_class=OpenStreetMapClass.ROAD).get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_overture_buildings():
    data = OvertureBuildings().get_data(BBOX)
    assert np.size(data) > 0
    assert_vector_stats(data, 'height', 1, 2.0, 12.5, 1079, 145)
    assert get_projection_name(data.crs.srs) == 'utm'
    utm_bbox_data = OvertureBuildings().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_overture_buildings_height():
    data = OvertureBuildingsHeight(CITY_CODE_FOR_BBOX).get_data(BBOX)
    assert np.size(data) > 0
    assert_vector_stats(data, 'overture_height', 1, 2.0, 12.5, 1079, 145)
    assert get_projection_name(data.crs.srs) == 'utm'
    utm_bbox_data = OvertureBuildingsHeight(CITY_CODE_FOR_BBOX).get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_overture_buildings_height_raster():
    data = OvertureBuildingsHeightRaster(CITY_CODE_FOR_BBOX).get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, -999.0, 12.5, 978604, 0)
    assert get_projection_name(data.rio.crs.to_epsg()) == 'utm'
    utm_bbox_data = OvertureBuildingsHeightRaster(CITY_CODE_FOR_BBOX).get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_protected_areas():
    data = ProtectedAreas().get_data(BBOX)
    assert np.size(data) > 0
    assert_vector_stats(data, 'protected', 0, 1, 1, 1, 0)
    assert get_projection_name(data.crs.srs) == 'utm'
    utm_bbox_data = ProtectedAreas().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_pop_weighted_pm2p5():
    data = PopWeightedPM2p5().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 6.57, 6.57, 1, 0)
    assert get_projection_name(data.rio.crs.to_epsg()) == 'utm'
    utm_bbox_data = PopWeightedPM2p5().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_riparian_areas():
    data = RiparianAreas().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, False, True, 1122, 0)
    assert get_projection_name(data.rio.crs.to_epsg()) == 'utm'
    utm_bbox_data = RiparianAreas().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

@pytest.mark.skip(reason="layer is deprecated")
def test_sentinel_2_level2():
    sentinel_2_bands = ["green"]
    data = Sentinel2Level2(sentinel_2_bands).get_data(BBOX)
    assert np.size(data.green) > 0
    # TODO Add value testing
    assert get_projection_name(data.spatial_ref.crs_wkt) == 'utm'
    utm_bbox_data = Sentinel2Level2(sentinel_2_bands).get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_smart_surface_lulc():
    data = SmartSurfaceLULC().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 1.0, 50.0, 979700, 0)
    assert get_projection_name(data.rio.crs.to_epsg()) == 'utm'
    utm_bbox_data = SmartSurfaceLULC().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_tree_canopy_cover_mask():
    data = TreeCanopyCoverMask().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.rio.crs.to_epsg()) == 'utm'
    utm_bbox_data = TreeCanopyCoverMask().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_tree_canopy_height():
    data = TreeCanopyHeight().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 0.0, 33.0, 976626, 0)
    assert get_projection_name(data.rio.crs.to_epsg()) == 'utm'
    utm_bbox_data = TreeCanopyHeight().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_tree_cover():
    data = TreeCover().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 0.0, 100.0, 9797, 0)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = TreeCover().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_urban_extents():
    data = UrbanExtents().get_data(BBOX)
    assert np.size(data) > 0
    assert_vector_stats(data, 'city_names', None, 'Portland', 'Portland', 1, 0)
    assert get_projection_name(data.crs.srs) == 'utm'
    utm_bbox_data = UrbanExtents().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_urban_land_use():
    data = UrbanLandUse().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 0.0, 5.0, 38986, 0)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = UrbanLandUse().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_ut_globus():
    data = UtGlobus(CITY_CODE_FOR_BBOX).get_data(BBOX)
    assert np.size(data) > 0
    assert_vector_stats(data, 'height', 0, 4, 12, 81, 0)
    assert get_projection_name(data.crs.srs) == 'utm'
    utm_bbox_data = UtGlobus(CITY_CODE_FOR_BBOX).get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_vegetation_water_map():
    data = VegetationWaterMap().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 2, 0.302, 0.998, 8737, 1060)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = VegetationWaterMap().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_world_pop():
    data = WorldPop().get_data(BBOX)
    assert np.size(data) > 0
    assert_raster_stats(data, 1, 0.0, 51.20, 100, 0)
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = WorldPop().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))


def _eval_numeric(sig_digits, data_min_notnull_val, data_max_notnull_val, data_notnull_count, data_null_count,
                  min_notnull_val, max_notnull_val, notnull_count, null_count):
    float_tol = (10 ** -sig_digits)
    is_matched = (math.isclose(data_min_notnull_val, min_notnull_val, rel_tol=float_tol)
                  and math.isclose(data_max_notnull_val, max_notnull_val, rel_tol=float_tol)
                  and data_notnull_count == notnull_count
                  and data_null_count == null_count
                  )

    expected = (f"{min_notnull_val:.{sig_digits}f}, {max_notnull_val:.{sig_digits}f}, {notnull_count}, {null_count}")
    actual = (f"{data_min_notnull_val:.{sig_digits}f}, {data_max_notnull_val:.{sig_digits}f}, {data_notnull_count}, {data_null_count}")

    return is_matched, expected, actual

def _eval_string(data_min_notnull_val, data_max_notnull_val, data_notnull_count, data_null_count,
                  min_notnull_val, max_notnull_val, notnull_count, null_count):

    is_matched = (data_min_notnull_val == min_notnull_val
                  and data_max_notnull_val == max_notnull_val
                  and data_notnull_count == notnull_count
                  and data_null_count == null_count
                  )

    expected = (f"{min_notnull_val}, {max_notnull_val}, {notnull_count}, {null_count}")
    actual = (f"{data_min_notnull_val}, {data_max_notnull_val}, {data_notnull_count}, {data_null_count}")
    return is_matched, expected, actual

def assert_vector_stats(data, attribute, sig_digits:int, min_notnull_val, max_notnull_val, notnull_count, null_count):
    data_min_notnull_val = data[attribute].dropna().min()
    data_max_notnull_val = data[attribute].dropna().max()
    data_notnull_count = data[attribute].notnull().sum()
    data_null_count = data[attribute].isnull().sum()

    if sig_digits is None:
        is_matched, expected, actual = _eval_string(data_min_notnull_val, data_max_notnull_val, data_notnull_count, data_null_count,
                         min_notnull_val, max_notnull_val, notnull_count, null_count)
    else:
        is_matched, expected, actual = _eval_numeric(sig_digits, data_min_notnull_val, data_max_notnull_val, data_notnull_count, data_null_count,
                                                     min_notnull_val, max_notnull_val, notnull_count, null_count)

    assert is_matched, f"expected ({expected}), but got ({actual})"

    # template
    # assert_vector_stats(data, 'attribute', None, 'minval', 'maxval', 1, 0)


def assert_raster_stats(data, sig_digits:int, min_notnull_val, max_notnull_val, notnull_count:int, null_count:int):
    data_min_notnull_val = np.nanmin(data)
    data_max_notnull_val = np.nanmax(data)
    data_notnull_count = data.count().item()
    data_null_count = data.isnull().sum().item()

    is_matched, expected, actual = _eval_numeric(sig_digits, data_min_notnull_val, data_max_notnull_val,
                  data_notnull_count, data_null_count, min_notnull_val, max_notnull_val, notnull_count, null_count)
    assert is_matched, f"expected ({expected}), but got ({actual})"

    # template
    # assert_raster_stats(data, 2, 0, 0, 1, 0)
