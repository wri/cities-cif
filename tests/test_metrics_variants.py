import pytest

from city_metrix import Era5MetPreprocessingUPenn
from tests.conftest import USA_OR_PORTLAND_ZONE

def test_era_5_met_preprocess_upenn_none_year():
    with pytest.raises(Exception) as e_info:
        Era5MetPreprocessingUPenn(start_date=None, end_date=None).get_metric(USA_OR_PORTLAND_ZONE)
    expected_exception = "Invalid date specification: start_date:None, end_date:None."
    msg_correct = False if str(e_info.value).find(expected_exception) == -1 else True
    assert msg_correct
