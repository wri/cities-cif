from datetime import datetime

from city_metrix import Era5MetPreprocessingUPenn, Era5MetPreprocessingUmep
from tests.conftest import USA_OR_PORTLAND_ZONE

def test_era_5_met_preprocess_upenn_none_year():
    indicator = Era5MetPreprocessingUPenn(year=None).get_metric(USA_OR_PORTLAND_ZONE)
    assert len(indicator) == 24
    retrieved_year = indicator.loc[0,'Year']
    expected_year = datetime.now().year - 1
    assert retrieved_year == expected_year

def test_era_5_met_preprocess_umep_none_year():
    indicator = Era5MetPreprocessingUmep(year=None).get_metric(USA_OR_PORTLAND_ZONE)
    assert len(indicator) == 24
    retrieved_year = indicator.loc[0, 'time'].year
    expected_year = datetime.now().year - 1
    assert retrieved_year == expected_year

def test_era_5_met_preprocess_upenn_no_year():
    import inspect
    signature = inspect.signature(Era5MetPreprocessingUPenn)
    param = signature.parameters.get('year')
    expected_year = param.default

    indicator = Era5MetPreprocessingUPenn().get_metric(USA_OR_PORTLAND_ZONE)
    assert len(indicator) == 24
    retrieved_year = indicator.loc[0,'Year']

    assert retrieved_year == expected_year

def test_era_5_met_preprocess_upenn_year_2020():
    sampling_year = 2020
    indicator = Era5MetPreprocessingUPenn(year=sampling_year).get_metric(USA_OR_PORTLAND_ZONE)
    assert len(indicator) == 24
    retrieved_year = indicator.loc[0,'Year']
    assert retrieved_year == sampling_year

def test_era_5_met_preprocess_umep_year_2020():
    sampling_year = 2020
    indicator = Era5MetPreprocessingUmep(year=sampling_year).get_metric(USA_OR_PORTLAND_ZONE)
    assert len(indicator) == 24
    retrieved_year = indicator.loc[0, 'time'].year
    assert retrieved_year == sampling_year
