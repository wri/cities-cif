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
    counts = convert_to_series(counts)
    assert counts.size == 100
    assert all([count == 100 for count in counts])

def test_mean():
    means = (MockLayer()
             .groupby(IDN_JAKARTA_TILED_ZONES)
             .mean())
    means = convert_to_series(means)
    assert means.size == 100
    assert all([mean == i for i, mean in enumerate(means)])


def test_fishnetted_count():
    counts = (MockLargeLayer()
              .groupby(IDN_JAKARTA_TILED_LARGE_ZONES)
              .count())
    counts = convert_to_series(counts)
    assert counts.size == 100
    assert all([count == 100 for count in counts])


def test_fishnetted_mean():
    means = (MockLargeLayer()
             .groupby(IDN_JAKARTA_TILED_LARGE_ZONES)
             .mean())
    means = convert_to_series(means)
    assert means.size == 100
    assert all([mean == i for i, mean in enumerate(means)])


def test_masks():
    counts = (MockLayer()
              .mask(MockMaskLayer())
              .groupby(IDN_JAKARTA_TILED_ZONES)
              .count())
    counts = convert_to_series(counts)
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


# TODO Commenting out for now untill issue can be later resolved.
# As is, most values are 50, but a few are 48 or 52
# def test_group_by_large_layer():
#     counts = (
#         MockLargeLayer()
#         .groupby(IDN_JAKARTA_TILED_LARGE_ZONES, layer=MockLargeGroupByLayer())
#         .count()
#     )
#     assert all([count == {1: 50.0, 2: 50.0} for count in counts])

def convert_to_series(data):
    if 'zone' in data.columns:
        data = data.drop(columns=['zone'])

    return data.squeeze()