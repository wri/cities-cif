import tempfile
from enum import Enum

import pytest
import os

from tests.tools.general_tools import create_target_folder, is_valid_path

class DumpRunLevel(Enum):
    RUN_NONE = 0
    RUN_FAST_ONLY = 1
    RUN_SLOW_ONLY = 2


# DUMP_RUN_LEVEL is the master control for when  to execute tests decorated with
# pytest.mark.skipif based on the DumpRunLevel enum class.
DUMP_RUN_LEVEL = DumpRunLevel.RUN_NONE

# Define a WGS bbox or otherwise a utm bbox
USE_WGS_BBOX = True

# Specify None to write to a temporary default folder otherwise specify a valid custom target path.
CUSTOM_DUMP_DIRECTORY = None

def pytest_configure(config):

    if DUMP_RUN_LEVEL is True:
        source_folder = os.path.dirname(__file__)
        target_folder = get_target_folder_path()
        create_target_folder(target_folder, False)

        print("\n\033[93m Layer files written to folder %s.\033[0m\n" % target_folder)

@pytest.fixture
def target_folder():
    return get_target_folder_path()

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

