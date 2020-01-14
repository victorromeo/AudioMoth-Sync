import unittest
from .context import camera
from datetime import datetime, timezone

class TestCamera(unittest.TestCase):
    def test_init(self):
        c = camera.camera()
        self.assertIsNotNone(c)

    def test_image_filename(self):
        c = camera.camera()
        d = datetime(2000,1,2,3,4,5,6)
        path = '/abc/def'
        self.assertEqual(c.image_filename(path,d), '/abc/def/20000102_030405.jpg')

    def test_click(self):
        c = camera.camera()
        c.click()