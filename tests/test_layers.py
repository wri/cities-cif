import pytest
import numpy as np
from city_metrix.layers import (
    Albedo,
    AlosDSM,
    AverageNetBuildingHeight,
    NdviSentinel2,
    EsaWorldCover,
    EsaWorldCoverClass,
    HighLandSurfaceTemperature,
    ImperviousSurface,
    LandsatCollection2,
    LandSurfaceTemperature,
    NasaDEM,
    NaturalAreas,
    OpenBuildings,
    OpenStreetMap,
    OpenStreetMapClass,
    OvertureBuildings,
    Sentinel2Level2,
    SmartSurfaceLULC,
    TreeCanopyHeight,
    TreeCover,
    UrbanLandUse,
    WorldPop
)
from tests.resources.bbox_constants import BBOX_BRA_LAURO_DE_FREITAS_1

# Tests are implemented for the same bounding box in Brazil.
COUNTRY_CODE_FOR_BBOX = 'BRA'
BBOX = BBOX_BRA_LAURO_DE_FREITAS_1

def test_albedo():
    data = Albedo().get_data(BBOX)
    assert np.size(data) > 0

def test_alos_dsm():
    data = AlosDSM().get_data(BBOX)
    assert np.size(data) > 0

def test_average_net_building_height():
    data = AverageNetBuildingHeight().get_data(BBOX)
    assert np.size(data) > 0

def test_esa_world_cover():
    land_cover_class = EsaWorldCoverClass.BUILT_UP
    data = EsaWorldCover(land_cover_class=land_cover_class).get_data(BBOX)
    assert np.size(data) > 0

def test_high_land_surface_temperature():
    data = HighLandSurfaceTemperature().get_data(BBOX)
    assert np.size(data) > 0

def test_impervious_surface():
    data = ImperviousSurface().get_data(BBOX)
    assert data.any()

def test_land_surface_temperature():
    data = LandSurfaceTemperature().get_data(BBOX)
    assert np.size(data) > 0

@pytest.mark.skip(reason="layer is deprecated")
def test_landsat_collection_2():
    bands = ["blue"]
    data = LandsatCollection2(bands).get_data(BBOX)
    assert np.size(data) > 0

def test_nasa_dem():
    data = NasaDEM().get_data(BBOX)
    assert np.size(data) > 0

def test_natural_areas():
    data = NaturalAreas().get_data(BBOX)
    assert np.size(data) > 0

def test_ndvi_sentinel2():
    data = NdviSentinel2(year=2023).get_data(BBOX)
    assert np.size(data) > 0

def test_openbuildings():
    data = OpenBuildings(COUNTRY_CODE_FOR_BBOX).get_data(BBOX)
    assert np.size(data) > 0

def test_open_street_map():
    data = OpenStreetMap(osm_class=OpenStreetMapClass.ROAD).get_data(BBOX)
    assert np.size(data) > 0

def test_overture_buildings():
    data = OvertureBuildings().get_data(BBOX)
    assert np.size(data) > 0

@pytest.mark.skip(reason="layer is deprecated")
def test_sentinel_2_level2():
    sentinel_2_bands = ["green"]
    data = Sentinel2Level2(sentinel_2_bands).get_data(BBOX)
    assert np.size(data) > 0

def test_smart_surface_lulc():
    data = SmartSurfaceLULC().get_data(BBOX)
    assert np.size(data) > 0

def test_tree_canopy_height():
    data = TreeCanopyHeight().get_data(BBOX)
    assert np.size(data) > 0

def test_tree_cover():
    data = TreeCover().get_data(BBOX)
    assert np.size(data) > 0

def test_urban_land_use():
    data = UrbanLandUse().get_data(BBOX)
    assert np.size(data) > 0

def test_world_pop():
    data = WorldPop().get_data(BBOX)
    assert np.size(data) > 0
