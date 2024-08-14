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

