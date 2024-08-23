import os
import tempfile

def create_temp_folder(sub_directory_name: str, delete_existing_files: bool):
    scratch_dir_name = tempfile.TemporaryDirectory().name
    dirpath = os.path.dirname(scratch_dir_name)
    temp_dir = os.path.join(dirpath, sub_directory_name)

    _create_target_folder(temp_dir, delete_existing_files)

    return temp_dir

def create_folder(folder_path, delete_existing_files: bool):
    if _is_valid_path(folder_path) is False:
        raise ValueError(f"The custom path '%s' is not valid. Stopping." % folder_path)
    _create_target_folder(folder_path, delete_existing_files)
    return folder_path

def _is_valid_path(path: str):
    return os.path.exists(path)

def _create_target_folder(folder_path, delete_existing_files: bool):
    if os.path.isdir(folder_path) is False:
        os.makedirs(folder_path)
    elif delete_existing_files is True:
        _remove_all_files_in_directory(folder_path)

def _remove_all_files_in_directory(directory):
    # Iterate over all the files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            # Check if it is a file and remove it
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error: {e}")