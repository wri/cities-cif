import pytest

from city_metrix.layers import (
    Albedo,
    AlosDSM,
    AverageNetBuildingHeight,
    NdviSentinel2,
    EsaWorldCover,
    EsaWorldCoverClass,
    HighLandSurfaceTemperature,
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
    count = Albedo().get_data(BBOX).count()
    assert count


def test_alos_dsm():
    count = AlosDSM().get_data(BBOX).count()
    assert count


def test_average_net_building_height():
    count = AverageNetBuildingHeight().get_data(BBOX).count()
    assert count


def test_esa_world_cover():
    land_cover_class = EsaWorldCoverClass.BUILT_UP
    count = (
        EsaWorldCover(land_cover_class=land_cover_class)
        .get_data(BBOX)
        .count()
    )
    assert count


def test_high_land_surface_temperature():
    count = HighLandSurfaceTemperature().get_data(BBOX).count()
    assert count


def test_land_surface_temperature():
    count = LandSurfaceTemperature().get_data(BBOX).count()
    assert count


@pytest.mark.skip(reason="layer is deprecated")
def test_landsat_collection_2():
    bands = ["blue"]
    count = LandsatCollection2(bands).get_data(BBOX).count()
    assert count


def test_nasa_dem():
    count = NasaDEM().get_data(BBOX).count()
    assert count


def test_natural_areas():
    count = NaturalAreas().get_data(BBOX).count()
    assert count

def test_ndvi_sentinel2():
    count = NdviSentinel2(year=2023).get_data(BBOX).count()
    assert count


def test_openbuildings():
    count = OpenBuildings(COUNTRY_CODE_FOR_BBOX).get_data(BBOX).count()
    assert count


def test_open_street_map():
    count = (
        OpenStreetMap(osm_class=OpenStreetMapClass.ROAD)
        .get_data(BBOX)
        .count()
    )
    assert count


def test_overture_buildings():
    count = OvertureBuildings().get_data(BBOX).count()
    assert count


@pytest.mark.skip(reason="layer is deprecated")
def test_sentinel_2_level2():
    sentinel_2_bands = ["green"]
    count = Sentinel2Level2(sentinel_2_bands).get_data(BBOX).count()
    assert count


def test_smart_surface_lulc():
    count = SmartSurfaceLULC().get_data(BBOX).count()
    assert count

def test_tree_canopy_height():
    count = TreeCanopyHeight().get_data(BBOX).count()
    assert count

def test_tree_cover():
    count = TreeCover().get_data(BBOX).count()
    assert count


def test_urban_land_use():
    assert UrbanLandUse().get_data(BBOX).count()


def test_world_pop():
    count = WorldPop().get_data(BBOX).count()
    assert count
