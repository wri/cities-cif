import ee
import numpy as np
import pytest

from city_metrix.layers import (
    Albedo,
    AlosDSM,
    AverageNetBuildingHeight,
    EsaWorldCover,
    EsaWorldCoverClass,
    LandSurfaceTemperature,
    NasaDEM,
    OpenBuildings,
    OpenStreetMap,
    OpenStreetMapClass,
    OvertureBuildings,
    SmartSurfaceLULC,
    TreeCanopyHeight,
    TreeCover,
    UrbanLandUse,
    Era5HottestDay,
)
from city_metrix.layers.layer import get_image_collection

from .conftest import (
    LARGE_ZONES,
    ZONES,
    MockGroupByLayer,
    MockLargeGroupByLayer,
    MockLargeLayer,
    MockLayer,
    MockMaskLayer,
)
from .fixtures.bbox_constants import *


def test_count():
    counts = MockLayer().groupby(ZONES).count()
    assert counts.size == 100
    assert all([count == 100 for count in counts])


def test_mean():
    means = MockLayer().groupby(ZONES).mean()
    assert means.size == 100
    assert all([mean == i for i, mean in enumerate(means)])


def test_fishnetted_count():
    counts = MockLargeLayer().groupby(LARGE_ZONES).count()
    assert counts.size == 100
    assert all([count == 100 for count in counts])


def test_fishnetted_mean():
    means = MockLargeLayer().groupby(LARGE_ZONES).mean()
    assert means.size == 100
    assert all([mean == i for i, mean in enumerate(means)])


def test_masks():
    counts = MockLayer().mask(MockMaskLayer()).groupby(ZONES).count()
    assert counts.size == 100
    for i, count in enumerate(counts):
        if i % 2 == 0:
            assert np.isnan(count)
        else:
            assert count == 100


def test_group_by_layer():
    counts = MockLayer().groupby(ZONES, layer=MockGroupByLayer()).count()
    assert all([count == {1: 50.0, 2: 50.0} for count in counts])


def test_group_by_large_layer():
    counts = (
        MockLargeLayer().groupby(LARGE_ZONES, layer=MockLargeGroupByLayer()).count()
    )
    assert all([count == {1: 50.0, 2: 50.0} for count in counts])


def test_read_image_collection():
    ic = ee.ImageCollection("ESA/WorldCover/v100")
    data = get_image_collection(ic, BBOX_BRAZIL_LAURO_DE_FREITAS_1, 10, "test")

    expected_crs =  32724
    expected_x_dimension = 187
    expected_y_dimension = 199

    assert data.rio.crs == expected_crs
    assert data.dims == {"x": expected_x_dimension, "y": expected_y_dimension}


def test_read_image_collection_scale():
    ic = ee.ImageCollection("ESA/WorldCover/v100")
    data = get_image_collection(ic, BBOX_BRAZIL_LAURO_DE_FREITAS_1, 100, "test")
    assert data.dims == {"x": 19, "y": 20}


def test_tree_cover():
    actual = TreeCover().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).mean()
    expected = 54.0
    tolerance = 0.1
    assert (
        pytest.approx(expected, rel=tolerance) == actual
    )


def test_albedo():
    assert Albedo().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).mean()


def test_lst():
    mean = LandSurfaceTemperature().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).mean()
    assert mean


def test_esa():
    count = (
        EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
        .get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1)
        .count()
    )
    assert count


def test_average_net_building_height():
    assert AverageNetBuildingHeight().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).mean()


def test_open_street_map():
    count = (
        OpenStreetMap(osm_class=OpenStreetMapClass.ROAD)
        .get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1)
        .count()
        .sum()
    )
    assert count


def test_urban_land_use():
    assert UrbanLandUse().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).count()


def test_openbuildings():
    count = OpenBuildings().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).count().sum()
    assert count


def test_tree_canopy_hight():
    count = TreeCanopyHeight().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).count()
    assert count


def test_alos_dsm():
    mean = AlosDSM().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).mean()
    assert mean


def test_smart_surface_lulc():
    count = SmartSurfaceLULC().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).count()
    assert count


def test_overture_buildings():
    count = OvertureBuildings().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).count().sum()
    assert count


def test_nasa_dem():
    mean = NasaDEM().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).mean()
    assert mean

def test_era_5_hottest_day():
    mean = Era5HottestDay().get_data(BBOX_BRAZIL_LAURO_DE_FREITAS_1).mean()
    assert mean
