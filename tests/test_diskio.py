import unittest
from .context import diskio
from .context import cfg

class Test_DiskIO(unittest.TestCase):
    def test_diskio_init(self):
        dio = diskio()
        dio.check_disk()

    def test_diskio_listfiles(self):
        dio = diskio()
        dio.list_files(cfg.paths.recordings, pattern = "*.*")

    def test_diskio_create_folder_remove_folder(self):
        dio = diskio()
        dio.create_folder(f'{cfg.paths.root}/temp')

        dio.remove_folder(f'{cfg.paths.root}/temp')

    def test_diskio_transfer_files(self):
        dio = diskio()
        working_path = f'{cfg.paths.root}/temp'

        dio.create_folder(working_path)
        dio.sync_files(cfg.paths.recordings, working_path)
        dio.list_files(working_path)
        dio.remove_files(working_path, "*.*")
        dio.remove_folder(working_path)