from tests.resources.conftest import RESOLUTION_MTHD, FIXED_RESOLUTION, RESOLUTION_MULTIPLIER, \
    USE_WGS_BBOX
from tests.tools.general_tools import get_class_default_spatial_resolution


def get_test_resolution(cls):
    if RESOLUTION_MTHD == 'fixed':
        target_res = FIXED_RESOLUTION
    else:
        target_res = RESOLUTION_MULTIPLIER * get_class_default_spatial_resolution(cls)
    return target_res

def get_test_bbox(sample_box):
    bbox = sample_box if USE_WGS_BBOX else sample_box.as_geographic_bbox()
    return bbox
