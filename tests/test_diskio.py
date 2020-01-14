import unittest
from .context import diskio
from configuration import configuration as config

class Test_DiskIO(unittest.TestCase):
    def test_diskio_init(self):
        dio = diskio.diskio()
        dio.check_disk()

    def test_diskio_listfiles(self):
        dio = diskio.diskio()
        dio.list_files(config.local_audio_path)

    def test_diskio_create_folder_remove_folder(self):
        dio = diskio.diskio()
        dio.create_folder(config.root_path + '/test_dir')

        dio.remove_folder(config.root_path + '/test_dir')

    def test_diskio_transfer_files(self):
        dio = diskio.diskio()
        working_path = config.root_path + '/test_dir'

        dio.create_folder(working_path)
        dio.sync_files(config.local_audio_path, working_path)
        dio.remove_files(working_path, "*.*")
        dio.remove_folder(working_path)