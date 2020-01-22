import unittest
from .context import aws as aws
from lib.shell import output_shell
from lib.config import cfg

class TestAWS(unittest.TestCase):

    def _create_testfile(self):
        _, success = output_shell('touch ./tmp/testfile')
        self.assertTrue(success)

    def _remove_testfile(self):
        _, success = output_shell('rm ./tmp/testfile')
        self.assertTrue(success)

    def _remove_testpath(self):
        _, success = output_shell('rm -rf ./tmp')
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
        testfile_path_remote = '{0}/testfile'.format(cfg.network.aws_bucket_name)
        testfile_path_local = './tmp/testfile'
        result, success = a.Copy(testfile_path_remote, testfile_path_local)
        self.assertTrue(success)
        self.assertIsNotNone(result)
        
        self._remove_testfile()
        self._remove_testpath()