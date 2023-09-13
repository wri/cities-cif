from cities_indicators.core import get_indicators, Indicator
from cities_indicators.city import get_city

import pandas as pd
import pytest


def get_baseline(indicator_name):
    df = pd.read_csv("tests/fixtures/jakarta_baseline.csv")
    return df[["geo_id", indicator_name]]


def test_tree_cover_in_built_up_areas():
    jakarta = get_city("IDN-Jakarta")
    indicators = get_indicators(cities=[jakarta], indicators=[Indicator.BUILT_LAND_WITH_TREE_COVER])
    baseline_indicators = get_baseline("HEA_4_percentBuiltupWithoutTreeCover")

    for actual, baseline in zip(indicators["HEA_4_percentBuiltupWithoutTreeCover"], baseline_indicators["HEA_4_percentBuiltupWithoutTreeCover"]):
        assert pytest.approx(actual, abs=1) == baseline


def test_surface_reflectivity():
    jakarta = get_city("IDN-Jakarta")
    indicators = get_indicators(cities=[jakarta], indicators=[Indicator.SURFACE_REFLECTIVTY])[0]
    baseline_indicators = get_baseline("HEA_3_percentBuiltwLowAlbedo")

    for actual, baseline in zip(indicators["HEA_3_percentBuiltwLowAlbedo"], baseline_indicators["HEA_3_percentBuiltwLowAlbedo"]):
        assert pytest.approx(actual, abs=1) == baseline


def test_tree_cover():
    jakarta = get_city("IDN-Jakarta")
    indicators = get_indicators(cities=[jakarta], indicators=[Indicator.TREE_COVER])
    baseline_indicators = get_baseline("LND_2_percentTreeCover")

    for actual, baseline in zip(indicators["LND_2_percentTreeCover"], baseline_indicators["LND_2_percentTreeCover"]):
        assert pytest.approx(actual, abs=1) == baseline
