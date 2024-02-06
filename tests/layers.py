import ee

from city_metrix.layers import LandsatCollection2, Albedo, LandSurfaceTemperature, EsaWorldCover, EsaWorldCoverClass, TreeCover
from city_metrix.layers.layer import get_image_collection
from .conftest import MockLayer, MockMaskLayer, ZONES, LARGE_ZONES, MockLargeLayer


import pytest
import numpy as np


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


SAMPLE_BBOX = (-38.35530428121955, -12.821710300686393, -38.33813814352424, -12.80363249765361)


def test_read_image_collection():
    ic = ee.ImageCollection("ESA/WorldCover/v100")
    data = get_image_collection(ic, SAMPLE_BBOX, 10, "test")

    assert data.rio.crs == 32724
    assert data.dims == {'x': 187, 'y': 200}


def test_read_image_collection_scale():
    ic = ee.ImageCollection("ESA/WorldCover/v100")
    data = get_image_collection(ic, SAMPLE_BBOX, 100, "test")
    assert data.dims == {'x': 19, 'y': 20}


def test_tree_cover():
    assert pytest.approx(53.84184165912419, rel=0.001) == TreeCover().get_data(SAMPLE_BBOX).mean()


def test_albedo():
    assert Albedo().get_data(SAMPLE_BBOX).mean()


def test_lst():
    mean = LandSurfaceTemperature().get_data(SAMPLE_BBOX).mean()
    assert mean


def test_esa():
    count = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP).get_data(SAMPLE_BBOX).count()
    assert count
