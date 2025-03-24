import pytest
import numpy as np

from city_metrix.layers import *
from city_metrix.layers.layer_tools import get_projection_name
from tests.conftest import EXECUTE_IGNORED_TESTS
from tests.resources.bbox_constants import BBOX_BRA_LAURO_DE_FREITAS_1, BBOX_USA_OR_PORTLAND_2
from tests.tools.spatial_tools import get_rounded_gdf_geometry

# Tests are implemented for an area where we have LULC
# COUNTRY_CODE_FOR_BBOX = 'BRA'
# BBOX = BBOX_BRA_LAURO_DE_FREITAS_1
COUNTRY_CODE_FOR_BBOX = 'USA'
BBOX = BBOX_USA_OR_PORTLAND_2
BBOX_AS_UTM = BBOX.as_utm_bbox()

def test_acag_pm2p5():
    data = AcagPM2p5().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = AcagPM2p5().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_albedo():
    data = Albedo().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = Albedo().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_alos_dsm():
    data = AlosDSM().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = AlosDSM().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_average_net_building_height():
    data = AverageNetBuildingHeight().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = AverageNetBuildingHeight().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_built_up_height():
    data = BuiltUpHeight().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = BuiltUpHeight().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_cams_ghg():
    data = CamsGhg().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = CamsGhg().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason="CDS API needs personal access token file to run")
def test_cams():
    data = Cams().get_data(BBOX)
    assert np.size(data) > 0
    utm_bbox_data = Cams().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

@pytest.mark.skipif(EXECUTE_IGNORED_TESTS == False, reason="CDS API needs personal access token file to run")
def test_era_5_hottest_day():
    data = Era5HottestDay().get_data(BBOX)
    assert np.size(data) > 0
    utm_bbox_data = Era5HottestDay().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_esa_world_cover():
    land_cover_class = EsaWorldCoverClass.BUILT_UP
    data = EsaWorldCover(land_cover_class=land_cover_class).get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = EsaWorldCover(land_cover_class=land_cover_class).get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_height_above_nearest_drainage():
    data = HeightAboveNearestDrainage().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = HeightAboveNearestDrainage().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_high_land_surface_temperature():
    data = HighLandSurfaceTemperature().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = HighLandSurfaceTemperature().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_high_slope():
    data = HighSlope().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = HighSlope().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_impervious_surface():
    data = ImperviousSurface().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = ImperviousSurface().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_land_cover_glad():
    data = LandCoverGlad().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = LandCoverGlad().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_land_cover_habitat_glad():
    data = LandCoverHabitatGlad().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = LandCoverHabitatGlad().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_land_cover_habitat_change():
    data = LandCoverHabitatChangeGlad().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = LandCoverHabitatChangeGlad().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_land_cover_simplified_glad():
    data = LandCoverSimplifiedGlad().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = LandCoverSimplifiedGlad().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_land_surface_temperature():
    data = LandSurfaceTemperature().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = LandSurfaceTemperature().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_landsat_collection_2():
    bands = ["blue"]
    data = LandsatCollection2(bands).get_data(BBOX)
    assert np.size(data.blue) > 0

def test_nasa_dem():
    data = NasaDEM().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = NasaDEM().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_natural_areas():
    data = NaturalAreas().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.rio.crs.to_epsg()) == 'utm'
    utm_bbox_data = NaturalAreas().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_ndvi_sentinel2():
    data = NdviSentinel2(year=2023).get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = NdviSentinel2(year=2023).get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_openbuildings():
    data = OpenBuildings(COUNTRY_CODE_FOR_BBOX).get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs.srs) == 'utm'
    utm_bbox_data = OpenBuildings(COUNTRY_CODE_FOR_BBOX).get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_open_street_map():
    data = OpenStreetMap(osm_class=OpenStreetMapClass.ROAD).get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs.srs) == 'utm'
    utm_bbox_data = OpenStreetMap(osm_class=OpenStreetMapClass.ROAD).get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_overture_buildings():
    data = OvertureBuildings().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs.srs) == 'utm'
    utm_bbox_data = OvertureBuildings().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_protected_areas():
    data = ProtectedAreas().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs.srs) == 'utm'
    utm_bbox_data = ProtectedAreas().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_pop_weighted_pm2p5():
    data = PopWeightedPM2p5().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.rio.crs.to_epsg()) == 'utm'
    utm_bbox_data = PopWeightedPM2p5().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_riparian_areas():
    data = RiparianAreas().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.rio.crs.to_epsg()) == 'utm'
    utm_bbox_data = RiparianAreas().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

@pytest.mark.skip(reason="layer is deprecated")
def test_sentinel_2_level2():
    sentinel_2_bands = ["green"]
    data = Sentinel2Level2(sentinel_2_bands).get_data(BBOX)
    assert np.size(data.green) > 0
    assert get_projection_name(data.spatial_ref.crs_wkt) == 'utm'
    utm_bbox_data = Sentinel2Level2(sentinel_2_bands).get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_smart_surface_lulc():
    data = SmartSurfaceLULC().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.rio.crs.to_epsg()) == 'utm'
    utm_bbox_data = SmartSurfaceLULC().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_tree_canopy_height():
    data = TreeCanopyHeight().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.rio.crs.to_epsg()) == 'utm'
    utm_bbox_data = TreeCanopyHeight().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_tree_cover():
    data = TreeCover().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = TreeCover().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_urban_extents():
    data = UrbanExtents().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs.srs) == 'utm'
    utm_bbox_data = UrbanExtents().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_urban_land_use():
    data = UrbanLandUse().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = UrbanLandUse().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_vegetation_water_map():
    data = VegetationWaterMap().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = VegetationWaterMap().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))

def test_world_pop():
    data = WorldPop().get_data(BBOX)
    assert np.size(data) > 0
    assert get_projection_name(data.crs) == 'utm'
    utm_bbox_data = WorldPop().get_data(BBOX_AS_UTM)
    assert get_rounded_gdf_geometry(data, 1).equals(get_rounded_gdf_geometry(utm_bbox_data, 1))
