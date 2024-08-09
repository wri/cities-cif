import ee
import pytest

from city_metrix.layers import (
    Albedo,
    AlosDSM,
    AverageNetBuildingHeight,
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
from city_metrix.layers.layer import get_image_collection
from tests.fixtures.bbox_constants import BBOX_BRAZIL_LAURO_DE_FREITAS_1


def test_albedo():
    assert Albedo().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).mean()


def test_alos_dsm():
    mean = AlosDSM().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).mean()
    assert mean


def test_average_net_building_height():
    assert AverageNetBuildingHeight().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).mean()


def test_esa_world_cover():
    count = (
        EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
        .get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1)
        .count()
    )
    assert count


def test_read_image_collection():
    ic = ee.ImageCollection("ESA/WorldCover/v100")
    data = get_image_collection(ic, BBOX_BRAZIL_LAURO_DE_FREITAS_1, 10, "test")

    expected_crs = 32724
    expected_x_dimension = 187
    expected_y_dimension = 199

    assert data.rio.crs == expected_crs
    assert data.dims == {"x": expected_x_dimension, "y": expected_y_dimension}


def test_read_image_collection_scale():
    ic = ee.ImageCollection("ESA/WorldCover/v100")
    data = get_image_collection(ic, BBOX_BRAZIL_LAURO_DE_FREITAS_1, 100, "test")
    assert data.dims == {"x": 19, "y": 20}


def test_high_land_surface_temperature():
    data = HighLandSurfaceTemperature().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1)
    assert data.any()


def test_land_surface_temperature():
    mean_lst = LandSurfaceTemperature().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).mean()
    assert mean_lst


def test_landsat_collection_2():
    bands = ['green']
    data = LandsatCollection2(bands).get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1)
    assert data.any()


def test_nasa_dem():
    mean = NasaDEM().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).mean()
    assert mean


def test_natural_areas():
    data = NaturalAreas().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1)
    assert data.any()


def test_openbuildings():
    count = OpenBuildings().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).count().sum()
    assert count


def test_open_street_map():
    count = (
        OpenStreetMap(osm_class=OpenStreetMapClass.ROAD)
        .get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1)
        .count()
        .sum()
    )
    assert count


def test_overture_buildings():
    count = OvertureBuildings().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).count().sum()
    assert count


def test_sentinal_2_level2():
    sentinal_2_bands = ["green"]
    data = Sentinel2Level2(sentinal_2_bands).get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1)
    assert data.any()


def test_smart_surface_lulc():
    count = SmartSurfaceLULC().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).count()
    assert count


def test_tree_canopy_hight():
    count = TreeCanopyHeight().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).count()
    assert count


def test_tree_cover():
    actual = TreeCover().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).mean()
    expected = 54.0
    tolerance = 0.1
    assert (
            pytest.approx(expected, rel=tolerance) == actual
    )


def test_urban_land_use():
    assert UrbanLandUse().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).count()


def test_world_pop():
    data = WorldPop().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1)
    assert data.any()
