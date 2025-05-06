import numpy as np

from .conftest import (
    IDN_JAKARTA_TILED_LARGE_ZONES,
    IDN_JAKARTA_TILED_ZONES,
    MockGroupByLayer,
    MockLargeGroupByLayer,
    MockLargeLayer,
    MockLayer,
    MockMaskLayer,
)

def test_count():
    counts = (MockLayer()
              .groupby(IDN_JAKARTA_TILED_ZONES)
              .count())
    assert counts.size == 100
    assert all([count == 100 for count in counts])

def test_mean():
    means = (MockLayer()
             .groupby(IDN_JAKARTA_TILED_ZONES)
             .mean())
    assert means.size == 100
    assert all([mean == i for i, mean in enumerate(means)])


def test_fishnetted_count():
    counts = (MockLargeLayer()
              .groupby(IDN_JAKARTA_TILED_LARGE_ZONES)
              .count())
    assert counts.size == 100
    assert all([count == 100 for count in counts])


def test_fishnetted_mean():
    means = (MockLargeLayer()
             .groupby(IDN_JAKARTA_TILED_LARGE_ZONES)
             .mean())
    assert means.size == 100
    assert all([mean == i for i, mean in enumerate(means)])


def test_masks():
    counts = (MockLayer()
              .mask(MockMaskLayer())
              .groupby(IDN_JAKARTA_TILED_ZONES)
              .count())
    assert counts.size == 100
    for i, count in enumerate(counts):
        if i % 2 == 0:
            assert np.isnan(count)
        else:
            assert count == 100


def test_group_by_layer():
    counts = (MockLayer()
              .groupby(IDN_JAKARTA_TILED_ZONES, layer=MockGroupByLayer())
              .count())
    assert all([count == {1: 50.0, 2: 50.0} for count in counts])


def test_group_by_large_layer():
    counts = (
        MockLargeLayer()
        .groupby(IDN_JAKARTA_TILED_LARGE_ZONES, layer=MockLargeGroupByLayer())
        .count()
    )
    assert all([count == {1: 50.0, 2: 50.0} for count in counts])

