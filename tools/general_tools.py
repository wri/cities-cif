import os
import tempfile
import shutil

def create_temp_folder(sub_directory_name: str, delete_existing_files: bool):
    scratch_dir_name = tempfile.TemporaryDirectory().name
    dirpath = os.path.dirname(scratch_dir_name)
    temp_dir = os.path.join(dirpath, sub_directory_name)

    if os.path.isdir(temp_dir) is False:
        os.makedirs(temp_dir)
    elif delete_existing_files is True:
        shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

    return temp_dir
