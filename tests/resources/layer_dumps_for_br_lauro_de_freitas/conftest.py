import tempfile
import pytest
import os
import shutil
from collections import namedtuple

from tests.resources.bbox_constants import BBOX_BRA_LAURO_DE_FREITAS_1
from tests.tools.general_tools import create_target_folder, is_valid_path

# RUN_DUMPS is the master control for whether the writes and tests are executed
# Setting RUN_DUMPS to True turns on code execution.
# Values should normally be set to False in order to avoid unnecessary execution.
RUN_DUMPS = False

# Multiplier applied to the default spatial_resolution of the layer
# Use value of 1 for default resolution.
SPATIAL_RESOLUTION_MULTIPLIER = 1

# Both the tests and QGIS file are implemented for the same bounding box in Brazil.
COUNTRY_CODE_FOR_BBOX = 'BRA'
BBOX = BBOX_BRA_LAURO_DE_FREITAS_1

# Specify None to write to a temporary default folder otherwise specify a valid custom target path.
CUSTOM_DUMP_DIRECTORY = None

def pytest_configure(config):

    if RUN_DUMPS is True:
        source_folder = os.path.dirname(__file__)
        target_folder = get_target_folder_path()
        create_target_folder(target_folder, False)

        print("\n\033[93m Layer files written to folder %s.\033[0m\n" % target_folder)

@pytest.fixture
def target_folder():
    return get_target_folder_path()

@pytest.fixture
def target_spatial_resolution_multiplier():
    return SPATIAL_RESOLUTION_MULTIPLIER

@pytest.fixture
def bbox_info():
    bbox = namedtuple('bbox', ['bounds', 'country'])
    bbox_instance = bbox(bounds=BBOX, country=COUNTRY_CODE_FOR_BBOX)
    return bbox_instance

def get_target_folder_path():
    if CUSTOM_DUMP_DIRECTORY is not None:
        if is_valid_path(CUSTOM_DUMP_DIRECTORY) is False:
            raise ValueError(f"The custom path '%s' is not valid. Stopping." % CUSTOM_DUMP_DIRECTORY)
        else:
            output_dir = CUSTOM_DUMP_DIRECTORY
    else:
        sub_directory_name = 'test_result_tif_files'
        scratch_dir_name = tempfile.TemporaryDirectory(ignore_cleanup_errors=True).name
        dir_path = os.path.dirname(scratch_dir_name)
        output_dir = os.path.join(dir_path, sub_directory_name)

    return output_dir

def prep_output_path(output_folder, file_name):
    file_path = os.path.join(output_folder, file_name)
    if os.path.isfile(file_path):
        os.remove(file_path)
    return file_path

def verify_file_is_populated(file_path):
    is_populated = True if os.path.getsize(file_path) > 0 else False
    return is_populated

def get_file_count_in_folder(dir_path):
    count = 0
    for path in os.scandir(dir_path):
        if path.is_file():
            count += 1
    return count
