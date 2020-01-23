import unittest
from .context import aws as aws
from lib.shell import output_shell
from lib.config import cfg

class TestAWS(unittest.TestCase):

    def _create_testfile(self):
        _, success = output_shell(f'touch {cfg.paths.root}/tmp/testfile')
        self.assertTrue(success)

    def _remove_testfile(self):
        _, success = output_shell(f'rm -f {cfg.paths.root}/tmp/testfile')
        self.assertTrue(success)

    def _remove_testpath(self):
        _, success = output_shell(f'rm -rf {cfg.paths.root}/tmp/')
        self.assertTrue(success) 

    def test_00_prerequisites(self):
        self._create_testfile()
        self._remove_testfile()

    def test_list(self):
        a = aws()
        result, success = a.List(cfg.network.aws_bucket_name)
        self.assertTrue(success)
        self.assertIsNotNone(result)

    def test_copy(self):
        a = aws()
        testfile_path_remote = f'{cfg.network.aws_bucket_name}/testfile'
        testfile_path_local = f'{cfg.paths.root}/tmp/testfile'
        result, success = a.Copy(testfile_path_remote, testfile_path_local)
        self.assertTrue(success)
        self.assertIsNotNone(result)
        
        self._remove_testfile()
        self._remove_testpath()