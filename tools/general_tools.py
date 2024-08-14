import platform
import os

def create_temp_folder(sub_directory):
    if platform.system() == 'Linux':
        path = '/tmp/%s' % sub_directory
    elif platform.system() == 'Windows':
        localappdata_path = os.getenv("LOCALAPPDATA")
        path = r'%s\Temp\%s' % (localappdata_path, sub_directory)
    else:
        raise ValueError('Method not implemented for this OS.')

    if os.path.isdir(path) == False:
        os.makedirs(path)

    return path

def verify_file_is_populated(file_path):
    is_populated = True if os.path.getsize(file_path) > 0 else False
    return is_populated
